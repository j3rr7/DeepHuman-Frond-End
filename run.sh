#!/usr/local/bin/bash
cd /home/jere/DeepHuman
filename="$(basename "/home/jere/pyflask/michael.jpg")"
mv "/home/jere/pyflask/michael.jpg" "/home/jere/DeepHuman/examples/${filename}"
python2 main_prepare_natural_img.py --file "/home/jere/DeepHuman/examples/${filename}"&& \ 
python2 main_infer_natural_img.py --file "/home/jere/DeepHuman/examples/${filename}" &&\ 
