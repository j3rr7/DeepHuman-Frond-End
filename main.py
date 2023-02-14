from flask import Flask, request, redirect, render_template, send_from_directory
import os, time
import subprocess
import shutil
import zipfile

app = Flask(__name__, static_folder = 'static')

@app.route('/')
def index():
  return render_template('index.html')

@app.route('/', methods=['POST'])
def upload_file():
  file = request.files['file']
  filename = file.filename
  file.save(filename)

  # get absolute image directory and save to full_img_dir
  full_img_dir = os.path.abspath(filename)

  try:

    with open('./run.sh', 'w+') as f:
      f.write('#!/usr/local/bin/bash\n')
      f.write('cd /home/jere/DeepHuman\n')
      f.write('filename="$(basename "' + full_img_dir + '")"\n')
      f.write('mv "' + full_img_dir + '" "/home/jere/DeepHuman/examples/${filename}"\n')
      f.write('python2 main_prepare_natural_img.py --file "/home/jere/DeepHuman/examples/${filename}"' +'&& \\ \n')
      f.write('python2 main_infer_natural_img.py --file "/home/jere/DeepHuman/examples/${filename}"' + ' &&\\ \n')
      # f.write('cp "${filename}' + '__volume_out_out_detailed.obj" "/home/jere/pyflask/model.obj"\n')

    os.chmod('./run.sh', 0o755)

    if not os.path.exists('./run.sh'):
      print("Error: File not found.")

    result = subprocess.call(['sh', './run.sh'])

    print(result)

    base_path = "/home/jere/DeepHuman/examples/"
    base_name, extension = os.path.splitext(filename)
    zip_file_name = base_name + '.zip'
    out_dir = './static/downloads/' + zip_file_name
    
    # grab the model file and move it to static/downloads
    with zipfile.ZipFile(base_path + base_name + "_intermediate_prepare.zip", 'r') as file:
    # grab all files wih prefix *_smpl_2.obj inside the zip file
      for member in file.namelist():
          if member.endswith("_smpl_2.obj"):
              file.extract(member, path= "./tmp/" + os.getcwd())
              break

    src_path = "./tmp/"
    dir_path = "./static/downloads/"

    # get file named *_smpl_2.obj
    for root, dirs, files in os.walk(src_path):
        for file in files:
            if file.endswith("_smpl_2.obj"):
                file_path = os.path.join(root, file)
                shutil.move(file_path, dir_path + "model.obj")
    
    shutil.rmtree("./tmp")

    # zip all files with prefix base_name
    with zipfile.ZipFile(zip_file_name, 'w', zipfile.ZIP_DEFLATED) as zip_file:
      for root, dirs, files in os.walk(base_path):
        for file in files:
          if base_name in file:
            print("Zipping... ",file)
            file_path = os.path.join(root, file)
            zip_file.write(file_path, os.path.relpath(file_path, start=base_path))

    shutil.move(zip_file_name, './static/downloads')

    # return 'done <a href="' + out_dir + '">Click Here</a> to download zip file <a href="/">Click Here</a> to try a different image'
    return render_template('done.html', outdir=out_dir, model_filename="{filename}__volume_out_out_detailed.obj"), 200
  except Exception as e:
    print(e)
    return 'Input image MUST have at least 70% human body to be able to proceed <a href="/">Click Here</a> to try a different image'
  
@app.route('/done')
def done():
  return render_template('done.html'), 200

@app.errorhandler(404)
def page_not_found(err):
  return render_template('404.html'), 404

if __name__ == '__main__':
  app.run(debug=True)
