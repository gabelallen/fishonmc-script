# fishonmc-script
Made just for fun and to experiment with OpenCV.

Works as follows: 
1. Automatically fits itself to the window's resolution.
2. Detects the "CATCH" popup by monitoring sudden changes in the top portion of the screen. Once detected, it right-clicks to start reeling in.
3. Finds the golden box and checks whether it contains the blue progress bar. If the progress bar isn't present, it holds CTRL to keep reeling.
4. Once the fish is caught, the script waits 5 seconds, and loops back to step 1 to catch more fish.

This demo shows the script catching a legendary fish. The OpenCV bounding box is shown on the right.
![Catching a legendary fish](./fish.gif)
