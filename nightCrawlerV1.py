########*********########FIRST RUN LES WRIGHT'S & lEODJ'S CODE
########*********########THEN LET THE USER CHOOSE THE SETTINGS ON A SCROLLTHRU MENU 5 BUTTONS  (UP, DOWN, LEFT, RIGHT, SELECT)
########*********########AFTER CLOSING THE MENU YOU CAN CHOOSE BETWEEN OVERLAY, THERMAL, OR ANALOG CAMERA
  import cv2
  import numpy as np
  import argparse
  import time
  import io
  import RPi.GPIO as GPIO


# Define GPIO pins for buttons
BUTTONS = {
    'up': 17,
    'down': 27,
    'left': 22,
    'right': 23,
    'select': 24
}

# Set up each button pin as input with pull-up resistor
for button, 17 in BUTTONS.items():
    GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)

#We need to know if we are running on the Pi, because openCV behaves a little oddly on all the builds!
#https://raspberrypi.stackexchange.com/questions/5100/detect-that-a-python-program-is-running-on-the-pi
def is_raspberrypi():
    try:
        with io.open('/sys/firmware/devicetree/base/model', 'r') as m:
            if 'raspberry pi' in m.read().lower(): return True
    except Exception: pass
    return False

isPi = is_raspberrypi()

parser = argparse.ArgumentParser()
parser.add_argument("--device", type=int, default=0, help="Video Device number e.g. 0, use v4l2-ctl --list-devices")
args = parser.parse_args()

if args.device:
	dev = args.device
else:q
	dev = 0

###SAVE CREATED IMAGE TO Thermal CAPTURE
    #init THERMAL CAPTURE
    thermal_cap = cv2.VideoCapture(0)  #THERMAL
    ##Wait 5 secs?
    #init ANALOG video CAPTURE
    analog_cap = cv2.VideoCapture(1)  #Analog low light camera



    #pull in the video but do NOT automatically convert to RGB, else it breaks the temperature data!
    #https://stackoverflow.com/questions/63108721/opencv-setting-videocap-property-to-cap-prop-convert-rgb-generates-weird-boolean
    if isPi == True:
    	thermal_cap.set(cv2.CAP_PROP_CONVERT_RGB, 0.0)
        analog_cap.set(cv2.CAP_PROP_CONVERT_RGB, 0.0)
    else:
    	thermal_cap.set(cv2.CAP_PROP_CONVERT_RGB, False)
        analog_cap.set(cv2.CAP_PROP_CONVERT_RGB, False)

    #256x192 General settings
    width = 256 #Sensor width
    height = 192 #sensor height
    scale = 3 #scale multiplier
    newWidth = width*scale
    newHeight = height*scale
    alpha = 1.0 # Contrast control (1.0-3.0)
    colormap = 0
    font=cv2.FONT_HERSHEY_SIMPLEX
    dispFullscreen = False
    cv2.namedWindow('Thermal',cv2.WINDOW_GUI_NORMAL)
    cv2.resizeWindow('Thermal', newWidth,newHeight)
    rad = 0 #blur radius
    threshold = 2
    hud = True
    recording = False
    elapsed = "00:00:00"
    snaptime = "None"

    def rec():
    	now = time.strftime("%Y%m%d--%H%M%S")
    	#do NOT use mp4 here, it is flakey!
    	thermal_out = cv2.VideoWriter(now+'output.avi', cv2.VideoWriter_fourcc(*'XVID'),25, (newWidth,newHeight))
    	return(videoOut)

    def snapshot(heatmap):
    	#I would put colons in here, but it Win throws a fit if you try and open them!
    	now = time.strftime("%Y%m%d-%H%M%S")
    	snaptime = time.strftime("%H:%M:%S")
    	cv2.imwrite("TC001"+now+".png", heatmap)
    	return snaptime


    while(thermal_cap.isOpened()):
    	# Capture frame-by-frame
    	ret, frame = thermal_cap.read()
    	if ret == True:
    		imdata,thdata = np.array_split(frame, 2)
    		#now parse the data from the bottom frame and convert to temp!
    		#https://www.eevblog.com/forum/thermal-imaging/infiray-and-their-p2-pro-discussion/200/
    		#Huge props to LeoDJ for figuring out how the data is stored and how to compute temp from it.
    		#grab data from the center pixel...
    		hi = thdata[96][128][0]
    		lo = thdata[96][128][1]
    		#print(hi,lo)
    		lo = lo*256
    		rawtemp = hi+lo
    		#print(rawtemp)
    		temp = (rawtemp/64)-273.15
    		temp = round(temp,2)
    		#print(temp)
    		#break

    		#find the max temperature in the frame
    		lomax = thdata[...,1].max()
    		posmax = thdata[...,1].argmax()
    		#since argmax returns a linear index, convert back to row and col
    		mcol,mrow = divmod(posmax,width)
    		himax = thdata[mcol][mrow][0]
    		lomax=lomax*256
    		maxtemp = himax+lomax
    		maxtemp = (maxtemp/64)-273.15
    		maxtemp = round(maxtemp,2)


    		#find the lowest temperature in the frame
    		lomin = thdata[...,1].min()
    		posmin = thdata[...,1].argmin()
    		#since argmax returns a linear index, convert back to row and col
    		lcol,lrow = divmod(posmin,width)
    		himin = thdata[lcol][lrow][0]
    		lomin=lomin*256
    		mintemp = himin+lomin
    		mintemp = (mintemp/64)-273.15
    		mintemp = round(mintemp,2)

    		#find the average temperature in the frame
    		loavg = thdata[...,1].mean()
    		hiavg = thdata[...,0].mean()
    		loavg=loavg*256
    		avgtemp = loavg+hiavg
    		avgtemp = (avgtemp/64)-273.15
    		avgtemp = round(avgtemp,2)



    		# Convert the real image to RGB
    		bgr = cv2.cvtColor(imdata,  cv2.COLOR_YUV2BGR_YUYV)
    		#Contrast
    		bgr = cv2.convertScaleAbs(bgr, alpha=alpha)#Contrast
    		#bicubic interpolate, upscale and blur
    		bgr = cv2.resize(bgr,(newWidth,newHeight),interpolation=cv2.INTER_CUBIC)#Scale up!
    		if rad>0:
    			bgr = cv2.blur(bgr,(rad,rad))

    		#apply colormap
    		if colormap == 0:
    			heatmap = cv2.applyColorMap(bgr, cv2.COLORMAP_JET)
    			cmapText = 'Jet'
    		if colormap == 1:
    			heatmap = cv2.applyColorMap(bgr, cv2.COLORMAP_HOT)
    			cmapText = 'Hot'
    		if colormap == 2:
    			heatmap = cv2.applyColorMap(bgr, cv2.COLORMAP_MAGMA)
    			cmapText = 'Magma'
    		if colormap == 3:
    			heatmap = cv2.applyColorMap(bgr, cv2.COLORMAP_INFERNO)
    			cmapText = 'Inferno'
    		if colormap == 4:
    			heatmap = cv2.applyColorMap(bgr, cv2.COLORMAP_PLASMA)
    			cmapText = 'Plasma'
    		if colormap == 5:
    			heatmap = cv2.applyColorMap(bgr, cv2.COLORMAP_BONE)
    			cmapText = 'Bone'
    		if colormap == 6:
    			heatmap = cv2.applyColorMap(bgr, cv2.COLORMAP_SPRING)
    			cmapText = 'Spring'
    		if colormap == 7:
    			heatmap = cv2.applyColorMap(bgr, cv2.COLORMAP_AUTUMN)
    			cmapText = 'Autumn'
    		if colormap == 8:
    			heatmap = cv2.applyColorMap(bgr, cv2.COLORMAP_VIRIDIS)
    			cmapText = 'Viridis'
    		if colormap == 9:
    			heatmap = cv2.applyColorMap(bgr, cv2.COLORMAP_PARULA)
    			cmapText = 'Parula'
    		if colormap == 10:
    			heatmap = cv2.applyColorMap(bgr, cv2.COLORMAP_RAINBOW)
    			heatmap = cv2.cvtColor(heatmap, cv2.COLOR_BGR2RGB)
    			cmapText = 'Inv Rainbow'

    		#print(heatmap.shape)

    		# draw crosshairs
    		cv2.line(heatmap,(int(newWidth/2),int(newHeight/2)+20),\
    		(int(newWidth/2),int(newHeight/2)-20),(255,255,255),2) #vline
    		cv2.line(heatmap,(int(newWidth/2)+20,int(newHeight/2)),\
    		(int(newWidth/2)-20,int(newHeight/2)),(255,255,255),2) #hline

    		cv2.line(heatmap,(int(newWidth/2),int(newHeight/2)+20),\
    		(int(newWidth/2),int(newHeight/2)-20),(0,0,0),1) #vline
    		cv2.line(heatmap,(int(newWidth/2)+20,int(newHeight/2)),\
    		(int(newWidth/2)-20,int(newHeight/2)),(0,0,0),1) #hline
    		#show temp
    		cv2.putText(heatmap,str(temp)+' C', (int(newWidth/2)+10, int(newHeight/2)-10),\
    		cv2.FONT_HERSHEY_SIMPLEX, 0.45,(0, 0, 0), 2, cv2.LINE_AA)
    		cv2.putText(heatmap,str(temp)+' C', (int(newWidth/2)+10, int(newHeight/2)-10),\
    		cv2.FONT_HERSHEY_SIMPLEX, 0.45,(0, 255, 255), 1, cv2.LINE_AA)

    		if hud==True:
    			# display black box for our data
    			cv2.rectangle(heatmap, (0, 0),(160, 120), (0,0,0), -1)
    			# put text in the box
    			cv2.putText(heatmap,'Avg Temp: '+str(avgtemp)+' C', (10, 14),\
    			cv2.FONT_HERSHEY_SIMPLEX, 0.4,(0, 255, 255), 1, cv2.LINE_AA)

    			cv2.putText(heatmap,'Label Threshold: '+str(threshold)+' C', (10, 28),\
    			cv2.FONT_HERSHEY_SIMPLEX, 0.4,(0, 255, 255), 1, cv2.LINE_AA)

    			cv2.putText(heatmap,'Colormap: '+cmapText, (10, 42),\
    			cv2.FONT_HERSHEY_SIMPLEX, 0.4,(0, 255, 255), 1, cv2.LINE_AA)

    			cv2.putText(heatmap,'Blur: '+str(rad)+' ', (10, 56),\
    			cv2.FONT_HERSHEY_SIMPLEX, 0.4,(0, 255, 255), 1, cv2.LINE_AA)

    			cv2.putText(heatmap,'Scaling: '+str(scale)+' ', (10, 70),\
    			cv2.FONT_HERSHEY_SIMPLEX, 0.4,(0, 255, 255), 1, cv2.LINE_AA)

    			cv2.putText(heatmap,'Contrast: '+str(alpha)+' ', (10, 84),\
    			cv2.FONT_HERSHEY_SIMPLEX, 0.4,(0, 255, 255), 1, cv2.LINE_AA)


    			cv2.putText(heatmap,'Snapshot: '+snaptime+' ', (10, 98),\
    			cv2.FONT_HERSHEY_SIMPLEX, 0.4,(0, 255, 255), 1, cv2.LINE_AA)

    			if recording == False:
    				cv2.putText(heatmap,'Recording: '+elapsed, (10, 112),\
    				cv2.FONT_HERSHEY_SIMPLEX, 0.4,(200, 200, 200), 1, cv2.LINE_AA)
    			if recording == True:
    				cv2.putText(heatmap,'Recording: '+elapsed, (10, 112),\
    				cv2.FONT_HERSHEY_SIMPLEX, 0.4,(40, 40, 255), 1, cv2.LINE_AA)

    		#Yeah, this looks like we can probably do this next bit more efficiently!
    		#display floating max temp
    		if maxtemp > avgtemp+threshold:
    			cv2.circle(heatmap, (mrow*scale, mcol*scale), 5, (0,0,0), 2)
    			cv2.circle(heatmap, (mrow*scale, mcol*scale), 5, (0,0,255), -1)
    			cv2.putText(heatmap,str(maxtemp)+' C', ((mrow*scale)+10, (mcol*scale)+5),\
    			cv2.FONT_HERSHEY_SIMPLEX, 0.45,(0,0,0), 2, cv2.LINE_AA)
    			cv2.putText(heatmap,str(maxtemp)+' C', ((mrow*scale)+10, (mcol*scale)+5),\
    			cv2.FONT_HERSHEY_SIMPLEX, 0.45,(0, 255, 255), 1, cv2.LINE_AA)

    		#display floating min temp
    		if mintemp < avgtemp-threshold:
    			cv2.circle(heatmap, (lrow*scale, lcol*scale), 5, (0,0,0), 2)
    			cv2.circle(heatmap, (lrow*scale, lcol*scale), 5, (255,0,0), -1)
    			cv2.putText(heatmap,str(mintemp)+' C', ((lrow*scale)+10, (lcol*scale)+5),\
    			cv2.FONT_HERSHEY_SIMPLEX, 0.45,(0,0,0), 2, cv2.LINE_AA)
    			cv2.putText(heatmap,str(mintemp)+' C', ((lrow*scale)+10, (lcol*scale)+5),\
    			cv2.FONT_HERSHEY_SIMPLEX, 0.45,(0, 255, 255), 1, cv2.LINE_AA)
        ###maybe here were gonna hold the image generation but for now left on
        #display image
    		cv2.imshow('Thermal',heatmap)

    		if recording == True:
    			elapsed = (time.time() - start)
    			elapsed = time.strftime("%H:%M:%S", time.gmtime(elapsed))
    			#print(elapsed)
    			thermal_out.write(heatmap)

                #THIS WHOLE PART WILL BE REWRITTEN TO BE MADE A MENU INSIDE THE THERMAL VIEW CALIBRATION SCREEN
                #TO BE OPERATED BY THE 5 KEY KEYPAD CONTROLLER THAT COMES WITH THE FOXEER CAMERA (AND MANY MORE ANALOG FPV)
                		keyPress = cv2.waitKey(1)
                		if keyPress == ord('a'): #Increase blur radius
                			rad += 1
                		if keyPress == ord('z'): #Decrease blur radius
                			rad -= 1
                			if rad <= 0:
                				rad = 0

                		if keyPress == ord('s'): #Increase threshold
                			threshold += 1
                		if keyPress == ord('x'): #Decrease threashold
                			threshold -= 1
                			if threshold <= 0:
                				threshold = 0

                	    if keyPress == ord('d'): #Increase scale
                			scale += 1
                			if scale >=5:
                                	newWidth = width*scale
                				scale = 5
                			newHeight = height*scale
                			if dispFullscreen == False and isPi == False:
                				cv2.resizeWindow('Thermal', newWidth,newHeight)
                		if keyPress == ord('c'): #Decrease scale
                			scale -= 1
                			if scale <= 1:
                				scale = 1
                			newWidth = width*scale
                			newHeight = height*scale
                			if dispFullscreen == False and isPi == False:
                				cv2.resizeWindow('Thermal', newWidth,newHeight)

                		if keyPress == ord('q'): #enable fullscreen
                			dispFullscreen = True
                			cv2.namedWindow('Thermal',cv2.WND_PROP_FULLSCREEN)
                		cv2.setWindowProperty('Thermal',cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
                		if keyPress == ord('w'): #disable fullscreen
                			dispFullscreen = False
                			cv2.namedWindow('Thermal',cv2.WINDOW_GUI_NORMAL)
                			cv2.setWindowProperty('Thermal',cv2.WND_PROP_AUTOSIZE,cv2.WINDOW_GUI_NORMAL)
                			cv2.resizeWindow('Thermal', newWidth,newHeight)

                		if keyPress == ord('f'): #contrast+
                			alpha += 0.1
                			alpha = round(alpha,1)#fix round error
                			if alpha >= 3.0:
                				alpha=3.0
                		if keyPress == ord('v'): #contrast-
                			alpha -= 0.1
                			alpha = round(alpha,1)#fix round error
                			if alpha<=0:
                				alpha = 0.0


                		if keyPress == ord('h'):  #h to turn hud on and off
                			if hud==True:
                				hud=False
                			elif hud==False:
                				hud=True

                		if keyPress == ord('m'): #m to cycle through color maps
                			colormap += 1
                			if colormap == 11:
                				colormap = 0

                		if keyPress == ord('r') and recording == False: #r to start reording
                			videoOut = rec()
                			recording = True
                			start = time.time()
                		if keyPress == ord('t'): #f to finish reording
                			recording = False
                			elapsed = "00:00:00"

                	    if keyPress == ord('p'): #f to finish reording
                			snaptime = snapshot(heatmap)

                		if keyPress == ord('q'):
                			break

####
####
####DEFINING THE 2 VIDEO STREAMS AND CREATING A PICTURE IN PICTURE VIEW
####
####
        def overlay_videos(analog_cap, thermal_out, analogThermal_cap, mini_size=(160, 120), position=(10, 10)):
            # Open the main video and mini video


            # Get the properties of the main video
            analog_width = int(analog_cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            analog_height = int(analog_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            analog_fps = analog_cap.get(cv2.CAP_PROP_FPS)
            analog_fourcc = cv2.VideoWriter_fourcc(*'XVID')

            # Create a VideoWriter object to write the output video
            analogThermal_cap = cv2.VideoWriter(output_path, main_fourcc, main_fps, (main_width, main_height))

            while True:
                # Read frames from both videos
                ret_main, main_frame = analog_cap.read()
                ret_mini, mini_frame = thermal_cap.read()

                # Break the loop if any of the videos end
                if not ret_main or not ret_mini:
                    break

                # DEFINE size of the mini video frame
                mini_frame_resized = cv2.resize(mini_frame, mini_size)

                # Get the position where the mini frame will be placed on the main frame
                x_offset, y_offset = position
                x_end = x_offset + mini_size[0]
                y_end = y_offset + mini_size[1]

                # Overlay the mini frame on the main frame
                main_frame[y_offset:y_end, x_offset:x_end] = mini_frame_resized

                # Write the combined frame to the output video
                analogThermal.write(main_frame)

                # Display the combined frame (optional)
                cv2.imshow('Combined Video', main_frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

####
####
####
####SWITCHING FROM 3 DIFFERENT FEEDS
####

    # Function to switch between feeds
    def switch_feed(key):
        if key == ord('1'):
            return thermal_out
        elif key == ord('2'):
            return analog_cap
        elif key == ord('3'):
            return analogThermal_cap
        return None

    current_cap = analog_cap

    while True:
        ret, frame = current_cap.read()
        if not ret:
            break

        # Display the video feed
        cv2.imshow('analogThermal', frame)

          # Check for button presses
        #if GPIO.input(BUTTONS['select']) == GPIO.LOW:  # Select button pressed



        #if GPIO.input(BUTTONS['up']) == GPIO.LOW:  # Up button pressed
            # Handle up button press
        #    pass
        #if GPIO.input(BUTTONS['down']) == GPIO.LOW:  # Down button pressed
        # Handle down button press
        #    pass
        #if GPIO.input(BUTTONS['left']) == GPIO.LOW:  # Left button pressed
        # Handle left button press
        #    pass
        #if GPIO.input(BUTTONS['right']) == GPIO.LOW:  # Right button pressed
        # Handle right button press
        #pass



        # Check for key press to switch feeds
        #key = cv2.waitKey(1) & 0xFF
        #if key in [ord('1'), ord('2'), ord('3')]:
        #    current_cap = switch_feed(key)
        #elif key == ord('q'):
        #    break

    # Release resources
    analog_cap.release()
    thermal_cap.release()
    thermal_out.release()
    analogThermal.release()
    GPIO.cleanup()
    cv2.destroyAllWindows()
####
####
####END
####
####
