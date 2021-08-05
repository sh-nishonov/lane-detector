import cv2 as cv
import numpy as np

def grayscale(img):
    return cv.cvtColor(img, cv.COLOR_BGR2GRAY)

def gaussian_noise(img, kernel_size): 
   return cv.GaussianBlur(img, (kernel_size, kernel_size), 0)

def canny(img, low_threshold, high_threshold): 
   return cv.Canny(img, low_threshold, high_threshold)

def region_of_interest(img):
    height, width = img.shape


    vertices =  np.array([[
        (width*0.20, height),
        (width*0.50, height*0.7), 
        (width*0.6, height * 0.7), 
        (width*0.95, height)
        ]], np.int32)

   


    mask = np.zeros_like(img)

    
    ignore_mask_color = 255

    cv.fillPoly(mask, vertices, ignore_mask_color)

    masked_image = cv.bitwise_and(img, mask)
    return masked_image

def detect_line_segments(cropped_edges, img):
    
    rho = 1  # distance precision in pixel, i.e. 1 pixel
    angle = np.pi / 180  # angular precision in radian, i.e. 1 degree
    min_threshold = 20 # minimal of votes
    line_segments = cv.HoughLinesP(cropped_edges, rho, angle, min_threshold, 
                                   np.array([]), minLineLength=15, maxLineGap=5)
    

    line_img = np.zeros((img.shape[0], img.shape[1], 3), dtype=np.uint8)
    
    line_img = slope_lines(line_img,line_segments)
    return line_img

    

def draw_lines(image, lines, color=[255, 0, 0], thickness=15):
    for line in lines:
        for x1,y1,x2,y2 in line:
            cv.line(image, (x1, y1), (x2, y2), color, thickness)

def slope_lines(image,lines):
    
    img = image.copy()
    poly_vertices = []
    order = [0,1,3,2]

    left_lines = [] # Like /
    right_lines = [] # Like \
    for line in lines:
        for x1,y1,x2,y2 in line:

            if x1 == x2:
                pass #Vertical Lines
            else:
                m = (y2 - y1) / (x2 - x1) #slope
                c = y1 - m * x1

                if m < 0:
                    left_lines.append((m,c))
                elif m >= 0:
                    right_lines.append((m,c))

    left_line = np.average(left_lines, axis=0) # averaging line points
    right_line = np.average(right_lines, axis=0)

    print(left_line, right_line)
    if left_line.any() == None or right_line.any() == None:
        return

    for slope, intercept in [left_line, right_line]:

        #getting complete height of image in y1
        rows, cols = image.shape[:2]
        y1= int(rows) #image.shape[0]

        
        y2= int(rows*0.73) #int(0.6*y1)

        #we know that equation of line is y=mx +c so we can write it x=(y-c)/m
        x1=int((y1-intercept)/slope)
        x2=int((y2-intercept)/slope)
        poly_vertices.append((x1, y1))
        poly_vertices.append((x2, y2))
        draw_lines(img, np.array([[[x1,y1,x2,y2]]]))
    
    poly_vertices = [poly_vertices[i] for i in order]
    cv.fillPoly(img, pts = np.array([poly_vertices],'int32'), color = (0,255,0))
    return cv.addWeighted(image,1,img,0.4,0.)

def weighted_img(img, initial_img, alpha=0.8, beta=1., theta=0.):
   
    lines_edges = cv.addWeighted(initial_img, alpha, img, beta, theta)
    
    return lines_edges
    

def main():



    kernel_size = 5


    cap = cv.VideoCapture("texas1024x768.mp4")

    while(cap.isOpened()):
        fps = int(cap.get(cv.CAP_PROP_FPS))
        print(f'{int(fps)}')
        _, img = cap.read()
        font = cv.FONT_HERSHEY_SIMPLEX 
        
        cv.putText(img,  
                    'FPS: '+str(fps),  
                    (50, 50),  
                    font, 1,  
                    (0, 255, 255),  
                    2,  
                    cv.LINE_4)
        g_noise = gaussian_noise(img, kernel_size)
        cany = canny(grayscale(img), 80, 240)


        roi = region_of_interest(cany)
        line_segments = detect_line_segments(roi, img)
        output = weighted_img(line_segments, img)
        cv.imshow("Image", output)
        if cv.waitKey(10) & 0xFF == ord('q'):
            break
    cap.release()

    cv.destroyAllWindows()

if __name__=='__main__':
    main()




