# Created by Daniel Cappel (ww11506207)
# 7/11/2022
# Version 1.1


import os
import sys
import time
import random

from subprocess import Popen, PIPE

from PyQt6 import QtGui, QtWidgets
from PyQt6.QtGui import QRegion
from PyQt6.QtCore import Qt, QPropertyAnimation, QPoint, QEasingCurve, QSize, QTimer, QRect
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QGridLayout, QLabel, QRadioButton


os.environ['QT_FONT_DPI'] = "96" # Prevent system upscaling of the GUI
useRandomBackgrounds = False
debugMode = False

# These are configuration for the radio buttons. Fill these with the names 
# of the program/workload options you want included in that suite.
Minimal_Suite = [ 'Example Workload 2', 'Example Workload 5', 'Example Workload 8' ]
Balanced_Suite = [ 'Example Workload 2', 'Example Workload 3', 'Example Workload 5',
					'Example Workload 7', 'Example Workload 8' ]



def humanReadableTime( seconds ):

	""" Converts a time interval in seconds to a human-readable string of days/hours/minutes, etc. """

	result = []
	intervals = (
		('weeks', 604800),  # 60 * 60 * 24 * 7
		('days', 86400),    # 60 * 60 * 24
		('hours', 3600),    # 60 * 60
		('minutes', 60),
		('seconds', 1),
		)

	if seconds == 0:
		return '0 seconds'

	for name, count in intervals:
		value = seconds // count # Floor division; rounds down to full int
		if value:
			seconds -= value * count
			if value == 1:
				name = name.rstrip('s')
			result.append( "{} {}".format(int(value), name) )

	if len( result ) == 2:
		return '{} and {}'.format( result[0], result[1] )
	else:
		commaJoined = ', '.join( result )

		# Replace the last comma and space with an 'and'
		li = commaJoined.rsplit( ', ', 1 )
		return ', and '.join( li )



class AutoInstallerChooser( QMainWindow ):

	labelStyle = (
			'color: rgb(230, 250, 255);' # Mostly-White Blue-ish
		)

	def __init__( self, autoStartTimeout=0 ):
		super().__init__()

		# Set window properties
		self.setWindowTitle( 'Workload Installer' )
		self.setWindowFlags( Qt.WindowType.FramelessWindowHint )
		self.setAttribute( Qt.WidgetAttribute.WA_TranslucentBackground )

		self.scriptHomeFolder = os.path.dirname( __file__ )
		os.chdir( self.scriptHomeFolder )
		self.autoStartTimeout = autoStartTimeout
		self.totalOptions = 0

		if autoStartTimeout:
			self.closeAfterInstall = True
		else:
			self.closeAfterInstall = False

		# Build image filepaths
		self.imagePaths = {}
		imagesFolder = os.path.join( self.scriptHomeFolder, 'imgs' )
		for file in os.listdir( imagesFolder ):
			self.imagePaths[file[:-4]] = os.path.join( imagesFolder, file )

		# Load some images (so it doesn't have to be done repeatedly for each workload option)
		self.selectionBg = QtGui.QImage( self.imagePaths['optionBg'] )
		self.checkMark = QtGui.QImage( self.imagePaths['checkMark'] )
		self.selectionMask = QtGui.QImage( self.imagePaths['mask'] ).createAlphaMask()

		# Establish the main frame object to attach workload choices and the button frame
		self.mainFrame = QVBoxLayout()
		self.mainFrame.setAlignment( Qt.AlignmentFlag.AlignCenter ) # Align in the center of the bgWidget
		self.mainFrame.setContentsMargins( 0, 20, 0, 20 )

		# Add workload choices
		self.addWorkloadOption( 'Example Workload 1', 3, r"Example Workload 1\Demo Install Script.bat", r'Example Workload 1\Done.txt' )
		self.addWorkloadOption( 'Example Workload 2', 3, r"Example Workload 2\Demo Install Script.bat", r'Example Workload 2\Done.txt' )
		self.addWorkloadOption( 'Example Workload 3', 3, r"Example Workload 3\Demo Install Script.bat", r'Example Workload 3\Done.txt' )
		self.addWorkloadOption( 'Example Workload 4', 3, r"Example Workload 4\Demo Install Script.bat", r'Example Workload 4\Done.txt' )
		self.addWorkloadOption( 'Example Workload 5', 3, r"Example Workload 5\Demo Install Script.bat", r'Example Workload 5\Done.txt', 'This one has a tooltip!' )
		self.addWorkloadOption( 'Example Workload 6', 3, r"Example Workload 6\Demo Install Script.bat", r'Example Workload 6\Done.txt' )
		self.addWorkloadOption( 'Example Workload 7', 3, r"Example Workload 7\Demo Install Script.bat", r'Example Workload 7\Done.txt' )
		self.addWorkloadOption( 'Example Workload 8', 3, r"Example Workload 8\Demo Install Script.bat", r'Example Workload 8\Done.txt' )
		self.addWorkloadOption( 'Example Workload 9', 3, r"Example Workload 9\Demo Install Script.bat", r'Example Workload 9\Done.txt' )

		# Ensure at least some of the workload installers were found
		if self.totalOptions == 0:
			print( 'No workload installers could be found, and no options could be added to the GUI.' )
			sys.exit( 2 )

		# Add a little spacing between options (proportionally less if there are more options)
		spacing = ( 10 - self.totalOptions ) * 3
		if spacing < 0:
			spacing = 0
		optionHeight = 42 + spacing
		self.mainFrame.setSpacing( spacing )
		if debugMode:
			print( 'option height: {}    spacing: {}'.format(optionHeight, spacing) )

		# Load and resize the background image
		if useRandomBackgrounds:
			bgName = random.choice( ['bg1', 'bg2', 'bg3'] )
		else:
			bgName = 'bg1'
		pixmapBg = QtGui.QPixmap( self.imagePaths[bgName] )
		appWidth = pixmapBg.width()
		appHeight = ( self.totalOptions * optionHeight ) + 200
		if autoStartTimeout:
			appHeight += 30
		if debugMode:
			print( 'appheight: ' + str(appHeight) )
		appBg = pixmapBg.scaled( appWidth, appHeight )

		# Get display dimensions and center the program in the middle of the screen
		self.resize( appWidth, appHeight )
		qtRectangle = self.frameGeometry()
		if debugMode:
			print('screen 0 geometry: ', app.screens()[0].availableGeometry() )
		centerPoint = app.screens()[0].availableGeometry().center()
		qtRectangle.moveCenter( centerPoint )
		self.move( qtRectangle.topLeft() )

		# Attach the background and main frame widget
		bgWidget = QLabel()
		bgWidget.setPixmap( appBg )
		bgWidget.setLayout( self.mainFrame )
		self.setCentralWidget( bgWidget )

		# Add lower buttons to the interface
		buttonsFrame = QGridLayout()
		buttonsFrame.setContentsMargins( 50, 20, 50, 0 ) # Set (mostly) Left/Right margins
		buttonsFrame.setSpacing( 15 ) # Set inter-widget padding

		# Add the suite-selection radio buttons
		radioBtn = StyledRadioButton( "Minimal", self.suiteSelected )
		radioBtn.style = radioBtn.style.replace( 'imgs', imagesFolder.replace('\\', '/') ) 
		buttonsFrame.addWidget( radioBtn, 0, 0 )

		radioBtn = StyledRadioButton( "Balanced", self.suiteSelected, checked=True )
		buttonsFrame.addWidget( radioBtn, 0, 1 )

		radioBtn = StyledRadioButton( "Full", self.suiteSelected )
		buttonsFrame.addWidget( radioBtn, 0, 2 )

		self.customradioBtn = StyledRadioButton( "Custom", self.suiteSelected )
		buttonsFrame.addWidget( self.customradioBtn, 0, 3 )

		# Add total install time display
		self.totalTimeLabel = QLabel()
		self.totalTimeLabel.setStyleSheet( self.labelStyle )
		buttonsFrame.addWidget( self.totalTimeLabel, 1, 0, 1, 4, Qt.AlignmentFlag.AlignCenter )
		self.updateTotalTime()

		# Add the Install/Cancel buttons
		btn = StyledButton( self, 'Install' )
		btn.setMinimumSize( 130, 30 )
		btn.clicked.connect( self.installSelected )
		buttonsFrame.addWidget( btn, 2, 0, 1, 2 )

		btn = StyledButton( self, 'Cancel' )
		btn.setMinimumSize( 130, 30 )
		btn.clicked.connect( self.close )
		buttonsFrame.addWidget( btn, 2, 2, 1, 2 )

		# Add the timeout display
		self.autoStartCountdown = QTimer()
		if autoStartTimeout:
			self.countdownLabel = QLabel( 'Auto-start in ' + humanReadableTime(autoStartTimeout) )
			self.countdownLabel.setStyleSheet( self.labelStyle )
			buttonsFrame.addWidget( self.countdownLabel, 3, 0, 1, 4, Qt.AlignmentFlag.AlignCenter )

			# Create a timer to count down to the auto-start procedure
			self.autoStartCountdown.setInterval( 1000 )
			self.autoStartCountdown.timeout.connect( self.updateAutoStartLabel )
			self.autoStartCountdown.start()
		else:
			self.countdownLabel = None

		self.mainFrame.addLayout( buttonsFrame )

		# Animations when the program is idle
		self.idleAnimTimer = QTimer()
		self.idleAnimTimer.setInterval( 4000 )
		self.idleAnimTimer.timeout.connect( self.fireIdleAnim )
		self.idleAnimTimer.start()

	def addWorkloadOption( self, name, installTime, installer, checkInstallPath, toolTip='' ):

		""" Adds a workload selection (checkbox and name) to the GUI for the user to toggle. 
			Note that the 'installer' argument is relative to this script's directory. """

		# Construct and validate the installer filepath
		installerPath = os.path.join( self.scriptHomeFolder, installer )
		if not os.path.exists( installerPath ):
			print( 'Warning! Unable to find installer path for "{}".'.format(installerPath) )
			return

		# Add the workload to the interface
		checkInstallPath = os.path.join( self.scriptHomeFolder, checkInstallPath ) # Update from a relative to an absolute path
		wl = WorkloadSelection( self, name, installTime, installerPath, checkInstallPath )
		self.mainFrame.addWidget( wl )
		self.totalOptions += 1

		if toolTip:
			wl.setToolTip( toolTip )

	def suiteSelected( self ):

		""" Called whenever the suite radio buttons are changed. """

		radioButton = self.sender()
		if not radioButton.isChecked():
			return

		radioButton.repaint()
		iterDelay = .05

		if radioButton.suite == 'Minimal':
			for wl in self.findChildren( WorkloadSelection ):
				if wl.name in Minimal_Suite:
					wl.selected = True
					wl.repaint()
				elif not wl.isInstalled():
					wl.selected = False
					wl.repaint()
				time.sleep( iterDelay )

		elif radioButton.suite == 'Balanced':
			for wl in self.findChildren( WorkloadSelection ):
				if wl.name in Balanced_Suite:
					wl.selected = True
					wl.repaint()
				elif not wl.isInstalled():
					wl.selected = False
					wl.repaint()
				time.sleep( iterDelay )

		elif radioButton.suite == 'Full':
			for wl in self.findChildren( WorkloadSelection ):
				wl.selected = True
				wl.repaint()
				time.sleep( iterDelay )

		elif radioButton.suite != 'Custom':
			raise Exception( 'Invalid Suite selection: {}'.format(radioButton.suite) )

		if not radioButton.suite == 'Custom':
			for wl in self.findChildren( WorkloadSelection ):
				if wl.selected:
					# Trigger an animation on this workload
					wl.lines.append( -40 )
					wl.animTimer.start()

		self.resetIdleAnims()
		self.updateTotalTime()

	def getSelectedSuite( self ):

		""" Checks the radio buttons and returns the currently selected suite. """

		for btn in self.findChildren( QRadioButton ):
			if btn.isChecked():
				return btn.suite

	def updateTotalTime( self ):

		""" Updates the total installation time displayed to the user. 
			Should be called any time the selection of workloads changes. """

		totalTime = 0
		allSelected = True
		allInstalled = True

		for wl in self.findChildren( WorkloadSelection ):
			if wl.selected and not wl.isInstalled():
				allInstalled = False
				totalTime += wl.installTime
			elif not wl.selected:
				allSelected = False

		if allSelected and allInstalled:
			self.totalTimeLabel.setText( 'All workloads have been installed.' )
		elif allInstalled:
			self.totalTimeLabel.setText( 'All selected workloads have been installed.' )
		elif totalTime == 0:
			self.totalTimeLabel.setText( 'Nothing selected to install.' )
		else:
			self.totalTimeLabel.setText( 'Total installation time:  ' + humanReadableTime(totalTime) )

	def installSelected( self ):

		""" Iterates over all of the workload options and installs those that are selected. """

		# Ensure one or more workloads are selected and they are not all already installed
		nothingSelected = True
		allInstalled = True
		workloadOptions = self.findChildren( WorkloadSelection )
		for wl in workloadOptions:
			if wl.selected:
				nothingSelected = False
				if not wl.isInstalled():
					allInstalled = False
					break

		if nothingSelected:
			msg = QtWidgets.QMessageBox( self )
			msg.setWindowTitle( 'Nothing to install' )
			msg.setIcon( QtWidgets.QMessageBox.Icon.Warning )
			msg.setText( "No workloads are selected!" )
			msg.exec()
			return
		elif allInstalled:
			msg = QtWidgets.QMessageBox( self )
			msg.setWindowTitle( 'Nothing to install' )
			msg.setIcon( QtWidgets.QMessageBox.Icon.Warning )
			msg.setText( "All selected workloads are already installed!" )
			msg.exec()
			return

		# Minimize the window so it doesn't interfere with installation processes
		self.hide()

		# Iterate over the workload objects and install those that are enabled
		for wl in workloadOptions:
			if wl.selected and not wl.isInstalled():
				self.installWorkload( wl )

		print( 'All selected installations complete.' )

		# Unminimize the program (must be shown for close method below to work)
		self.show()

		# Close the program if it is being run in automation
		if self.closeAfterInstall and not debugMode:
			self.close()
		else:
			if self.countdownLabel:
				self.countdownLabel.setText( 'Installations complete.' )

			# Show the completion message window
			msg = QtWidgets.QMessageBox( self )
			msg.setWindowTitle( 'Installations complete!' )
			msg.setIcon( QtWidgets.QMessageBox.Icon.Information )
			msg.setText( "All selected installations have completed." )
			msg.exec()

	def installWorkload( self, wl ):

		""" Installs a given workload onto the SUT by running its installer in a new process. """

		if debugMode:
			print( '       -  -  -' )
			print( 'Running ' + wl.name + ' installer...' )

		# Get the current working directory for the target workload installer's directory
		wlDir = os.path.dirname( wl.installerPath )

		# Run the installer in a new process
		process = Popen( wl.installerPath, cwd=wlDir, stdout=PIPE, stderr=PIPE, shell=True, text=True )

		# Wait for the process to complete while printing output in real time
		startTime = time.perf_counter()
		timeout = 600
		output = process.stdout.readline()
		while output or process.poll() is None:
			output = output.strip() # Removes leading and trailing whitespace
			if output:
				print( output )
			elif time.perf_counter() - startTime >= timeout:
				print( 'Installation time exceeded the timeout!' )
				process.kill()
			else:
				time.sleep( .5 )
			output = process.stdout.readline()

		if debugMode:
			toc = time.perf_counter()
			print( 'Time to install {}: {}'.format(wl.name, toc-startTime) )

		# Report any errors
		returnCode = process.returncode
		if returnCode != 0:
			print( 'There was an error installing {}; error code {}'.format(wl.name, returnCode) )
			print( process.stderr.read().strip() )

	def mousePressEvent( self, event ):

		""" Used for dragging/positioning the window. """

		self.resetIdleAnims()
		self.abortAutoStart()
		self.oldPosition = event.globalPosition().toPoint()

	def mouseMoveEvent( self, event ):

		""" Used for dragging/positioning the window. """

		newPosition = event.globalPosition().toPoint()
		delta = QPoint( newPosition - self.oldPosition )
		self.move( self.x() + delta.x(), self.y() + delta.y() )
		self.oldPosition = newPosition

	def updateAutoStartLabel( self ):

		""" Used with automation to automatically start installations after a timeout period. """

		self.autoStartTimeout -= 1

		if self.autoStartTimeout > 0:
			self.countdownLabel.setText( 'Auto-start in ' + humanReadableTime(self.autoStartTimeout) )
		else:
			# Reached the timeout!
			self.autoStartCountdown.stop()
			self.countdownLabel.setText( 'Auto-starting installations...' )
			self.installSelected()

	def abortAutoStart( self ):

		""" Cancels the auto-start procedure. Should be called if the user interacts with 
			the program by clicking on any part of it. """

		if self.countdownLabel:
			self.autoStartCountdown.stop()
			self.countdownLabel.setText( 'User activity detected. Auto-start aborted.' )

	def resetIdleAnims( self ):

		""" Prevents idle animations while a user is interacting with the program. """

		self.idleAnimTimer.stop()
		self.idleAnimTimer.start()

	def fireIdleAnim( self ):

		""" During periods of no user inactivity, randomly pick
			two of the workload options and trigger their animation. """

		workloadOptions = self.findChildren( WorkloadSelection )
		randomOption = random.choice( workloadOptions )
		randomOption.enterEvent()



class StyledRadioButton( QtWidgets.QRadioButton ):

	font = QtGui.QFont( 'Trebuchet', pointSize=10, weight=QtGui.QFont.Weight.DemiBold )

	style = (
			'QRadioButton'
			'{'
				'color: rgb(230, 250, 255);' # Mostly-White Blue-ish
			'}'
			'QRadioButton::indicator'
			'{'
				'width: 24px;'
				'height: 16px;'
			'}'
			'QRadioButton::indicator::unchecked'
			'{'
				'image: url("imgs/rbUnchecked.png");'
			'}'
			'QRadioButton::indicator:unchecked:hover'
			'{'
				'image: url("imgs/rbHovered.png");'
			'}'
			'QRadioButton::indicator::checked '
			'{'
				'image: url("imgs/rbChecked.png");'
			'}'
			'QRadioButton::indicator:checked:hover '
			'{'
				'image: url("imgs/rbCheckedHovered.png");'
			'}'
		)

	def __init__( self, text, selectionHandler, checked=False ):
		super().__init__( text )

		self.suite = text
		self.setChecked( checked )
		self.setFont( self.font )

		self.setStyleSheet( self.style )
		self.setCursor( Qt.CursorShape.PointingHandCursor )

		self.toggled.connect( selectionHandler )



class StyledButton( QtWidgets.QPushButton ):

	font = QtGui.QFont( 'Trebuchet', pointSize=11, weight=QtGui.QFont.Weight.DemiBold )
	
	style = (
			'QPushButton {'
				'color: rgb(230, 250, 255);' # Mostly-White Blue-ish
				'background-image: url("REPLACE_ME!");'
				'background-position: center;'
				'background-repeat: no-repeat;'
				'padding: 3;'
				'margin: 5px;'
				'margin-left: 20px;'
				'margin-right: 20px;'
				'border-radius: 4px;'
				'border: 1px inset rgb(90, 218, 255);'
			'}'
		)

	def __init__( self, parent, text ):
		super().__init__( text )

		bgImagePath = parent.imagePaths['btn'].replace( '\\', '/' )
		self.style = self.style.replace( 'REPLACE_ME!', bgImagePath )

		self.setStyleSheet( self.style )
		self.setFont( self.font )

		self.anim = QPropertyAnimation( self, b"geometry" )
		self.anim.setEasingCurve( QEasingCurve.Type.Linear )
		self.anim.setDuration( 140 )

		self.origGeom = None
		self.largeGeom = None

	def enterEvent( self, event ):
		# Calculate new position/size
		if not self.largeGeom:
			self.origGeom = self.geometry()
			newX = self.origGeom.x() - 4
			newY = self.origGeom.y() - 3
			newW = self.origGeom.width() + 8
			newH = self.origGeom.height() + 6
			self.largeGeom = QRect( newX, newY, newW, newH )

		self.anim.setEndValue( self.largeGeom )
		self.anim.start()

	def leaveEvent( self, event ):
		if self.origGeom:
			self.anim.setEndValue( self.origGeom )
			self.anim.start()



class WorkloadSelection( QtWidgets.QLabel ):

	elBlue = QtGui.QColor( 90, 218, 255 ) # Electric Blue
	yellow = QtGui.QColor( 220, 207, 113 )
	fadedBlue = QtGui.QColor( 104, 139, 149 ) # Faded Blue
	whiteBlue = QtGui.QColor( 230, 250, 255 ) # Mostly-White Blue-ish

	def __init__( self, parent, name, installTime, installerPath, checkInstallPath ):
		super().__init__( parent )

		self.bg = parent.selectionBg
		self.mask = parent.selectionMask
		self.checkMark = parent.checkMark

		self.name = name
		self.installTime = installTime
		self.installerPath = installerPath
		self.checkInstallPath = checkInstallPath
		self.lines = [] # A list of base offsets or x-origins for the line(s)
		self.width = 450

		# Determine whether the workload should be selected by default
		if debugMode or self.isInstalled():
			self.selected = True
		else:
			self.selected = ( name in Balanced_Suite )

		# Format install time (seconds to 'min:sec')
		minutes = int( installTime / 60 ) # Rounds down
		seconds = installTime % 60
		if minutes >= 1:
			self.installTimeStr = '{}:{:0>2}'.format( minutes, seconds )
		else:
			self.installTimeStr = '{} s'.format( seconds )

		self.setMinimumSize( QSize(self.width, 42) )
		self.setCursor( Qt.CursorShape.PointingHandCursor )
		if debugMode: # Enable coords tooltip (enables self.mouseMoveEvent without needing to hold mouse-1)
			self.setMouseTracking( True )

		# Set up a clock to power animation loops
		self.animTimer = QTimer()
		self.animTimer.setInterval( 17 )
		self.animTimer.timeout.connect( self.repaint )

	def paintEvent( self, event ):
		painter = QtGui.QPainter( self )
		painter.drawImage( 0, 0, self.bg )
		isInstalled = self.isInstalled()

		# Set a white pen for font drawing
		pen = painter.pen()
		if self.selected or isInstalled:
			pen.setColor( self.whiteBlue )
		else:
			pen.setColor( self.fadedBlue )
		painter.setPen( pen )

		# Set a font for the workload name
		font = painter.font()
		font.setFamily( 'Sylfaen' )
		font.setBold( True )
		font.setPointSize( 14 )
		painter.setFont( font )
		painter.drawText( 90, 28, self.name )

		# Draw the time estimate
		font.setBold( False )
		font.setPointSize( 10 )
		painter.setFont( font )
		painter.drawText( 386, 26, self.installTimeStr )

		# Set a mask for applying the edge-line animation
		mask = QtGui.QBitmap.fromImage( self.mask )
		mask = QRegion( mask )
		painter.setClipRegion( mask )

		# Draw the edge-line animations
		if isInstalled:
			pen.setColor( self.yellow )
		else:
			pen.setColor( self.elBlue )
		lineUpdates = []
		for line in self.lines:
			xCoord = line + 10
			pen.setWidth( 14 )
			painter.setPen( pen )
			painter.drawLine( xCoord+30, 10, xCoord, 32 )

			pen.setWidth( 8 )
			painter.setPen( pen )
			painter.drawLine( xCoord+50, 10, xCoord+20, 32 )

			if xCoord < self.width:
				lineUpdates.append( xCoord )

		# Draw a checkmark on the left if this workload is installed
		if isInstalled:
			painter.setClipping( False )
			painter.drawImage( 40, 0, self.checkMark )

		# Update the lines list with new offsets (forgetting finished ones)
		self.lines = lineUpdates
		if not self.lines:
			self.animTimer.stop()

	def isInstalled( self ):
		if os.path.exists( self.checkInstallPath ):
			return True
		else:
			return False

	def mousePressEvent( self, event=None ):
		# Queue up an animation
		self.lines.append( -40 )
		self.animTimer.start()

		mainWindow = self.window()
		mainWindow.abortAutoStart()
		mainWindow.resetIdleAnims()

		# If this workload is not already installed, update/toggle the selection
		if not self.isInstalled():
			self.selected = not self.selected

			# Show this as a "Custom" installation suite
			mainWindow.customradioBtn.setChecked( True )
			mainWindow.updateTotalTime()

	def enterEvent( self, event=None ):
		self.lines.append( -40 )
		self.animTimer.start()
		self.window().resetIdleAnims()

	def mouseMoveEvent( self, event=None ):

		""" Tooltip to show mouse coordinates, for debugging/development. """

		position = event.position()
		toolTipPosition = self.mapToGlobal( position.toPoint() )
		toolTipPosition.setX( toolTipPosition.x()+10 )
		toolTipPosition.setY( toolTipPosition.y()-60 )
		text = f"x: {position.x()}\ny: {position.y()}"
		QtWidgets.QToolTip.showText( toolTipPosition, text )



if __name__ == "__main__":
	# Parse command line arguments
	if debugMode:
		print( 'CMD arguments: ' + str(sys.argv) )
	if len( sys.argv ) > 1:
		try:
			autoStartTimeout = int( sys.argv[1] )
		except:
			print( 'Invalid command line args; usage:' )
			print( '    "' + sys.argv + '" [autoStartTimeout]' )
			print( '' )
			print( 'The option "autoStartTimeout" should be an integer, and' )
			print( 'should indicate the number of seconds before the program' )
			print( 'automatically starts installations for the default suite.' )
			sys.exit( 1 )
	else:
		autoStartTimeout = 0

	# Start the interface
	app = QApplication( sys.argv )

	window = AutoInstallerChooser( autoStartTimeout )
	window.show()

	app.exec()