import cv2
import numpy as np
import sys

def detect_prism(image_path):

    img = cv2.imread(image_path)
    if img is None:
        print("Could not load image")
        return

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.createCLAHE(2.0,(8,8)).apply(gray)
    blur = cv2.GaussianBlur(gray,(5,5),0)

    edges = cv2.Canny(blur,50,150)

    lines = cv2.HoughLinesP(edges,1,np.pi/180,100,
                            minLineLength=100,
                            maxLineGap=20)

    if lines is None:
        print("No lines found")
        return

    # draw lines
    output = img.copy()
    for l in lines:
        x1,y1,x2,y2 = l[0]
        cv2.line(output,(x1,y1),(x2,y2),(0,255,0),2)

    # group parallel lines
    groups = group_parallel_lines(lines)

    print("Detected parallel groups:", len(groups))

    cv2.namedWindow("Edges", cv2.WINDOW_NORMAL)
    cv2.namedWindow("Lines", cv2.WINDOW_NORMAL)

    cv2.moveWindow("Edges", 0, 0)
    cv2.moveWindow("Lines", 950, 100)

    cv2.resizeWindow("Edges", 100, 50)
    cv2.resizeWindow("Lines", 800, 600)

    cv2.imshow("Edges", edges)
    cv2.imshow("Lines", output)

    cv2.waitKey(0)
    cv2.destroyAllWindows()

def line_angle(x1,y1,x2,y2):
    return np.arctan2((y2-y1),(x2-x1))


def group_parallel_lines(lines, threshold=np.pi/36):
    groups = []

    for l in lines:
        x1,y1,x2,y2 = l[0]
        angle = line_angle(x1,y1,x2,y2)

        added = False

        for g in groups:
            if abs(angle - g[0][4]) < threshold:
                g.append([x1,y1,x2,y2,angle])
                added = True
                break

        if not added:
            groups.append([[x1,y1,x2,y2,angle]])

    return groups


if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("Usage: python detect_prism.py image.png")
        sys.exit(1)

    detect_prism(sys.argv[1])