cat $(find results -maxdepth 1 -name "*.png" | sort -V) | ffmpeg -framerate 6 -i - -c:v libx264 -profile:v high -crf 20 -pix_fmt yuv420p linear_regression.mp4

