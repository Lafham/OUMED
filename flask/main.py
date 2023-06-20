import os
from subprocess import check_output
import subprocess 
from flask import Flask, request, render_template, send_file
from werkzeug.utils import secure_filename
import json
import xmltodict

from lxml import etree


UPLOAD_FOLDER = 'static'

app = Flask(__name__)
app.config['SECRET_KEY'] = "jjjj"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file_dtd(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() == 'dtd'
def allowed_file_xsd(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'xsd'}
def allowed_file_xml(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'xml'}


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/convertDTDtoXSD', methods=['GET', 'POST'])
def converDTDtoXSD():
    if request.method == "POST":
        error = ""
        fileDTD = request.files['fileDTD']
        filename = secure_filename(fileDTD.filename)
        fileDTD.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        # print(filename)
        dtd_file = "static/"+filename
        
        _, file_extension = os.path.splitext(fileDTD.filename)

        if file_extension == ".dtd" :
            try:
                pipe = check_output(["perl", "dtd2xsd.pl", dtd_file], stdin=subprocess.PIPE).decode("UTF-8")
                # ss = str(pipe.replace("b\"",""))
                print(pipe)
                f = open("xsdfile.xsd", "w")
                f.write(pipe)
                f.close()
                        
                return send_file("xsdfile.xsd",as_attachment=True)

            except :
                print('error')
        else:
            error = "Your file is not a .dtd File, Retry again !"
            return render_template('convertDTDtoXSD.html',error=error)
        
    return render_template('convertDTDtoXSD.html')


@app.route('/validateXSD', methods=['GET', 'POST'])
def validateXSD():
    if request.method == 'POST':
        fileXML = request.files['fileXML']
        fileXSD = request.files['fileXSD']
        res=[]
        
        _, file_extension_xml = os.path.splitext(fileXML.filename)
        _, file_extension_xsd = os.path.splitext(fileXSD.filename)

        if fileXSD and file_extension_xsd == ".xsd" and fileXML and file_extension_xml == ".xml":
            xml_file = etree.parse(fileXML)
            xsd_validator = etree.XMLSchema(file=fileXSD)

            is_valid = xsd_validator.validate(xml_file)

            if (is_valid):
                res = ["success","The File XML is Valid"]
                return render_template('validateXSD.html', res=res)
                # return "<h1>Is valid</h1>"
            else:
                res = ["error","The File XML is not Valid"]
                return render_template('validateXSD.html', res=res)
        else:
            res = ["error","One of your files is not Valid"]
            return render_template('validateXSD.html', res=res)

    return render_template('validateXSD.html',res="")


@app.route('/validateDTD', methods=['GET', 'POST'])
def validateDTD():
    res=[]
    if request.method == 'POST':
        fileXML = request.files['fileXML']
        fileDTD = request.files['fileDTD']

        _, file_extension_xml = os.path.splitext(fileXML.filename)
        _, file_extension_dtd = os.path.splitext(fileDTD.filename)

        if fileDTD and file_extension_dtd == ".dtd" and fileXML and file_extension_xml == ".xml":
            xml_file = etree.parse(fileXML)
            DTD_validator = etree.DTD(file=fileDTD)

            is_valid = DTD_validator.validate(xml_file)

            if (is_valid):
                res = ["success","The File XML is Valid"]
                return render_template('validateDTD.html', res=res)
            else:
                res = ["error","The File XML is not Valid"]
                return render_template('validateDTD.html', res=res)
        else:
            res = ["error","One of your files is not Valid"]
            return render_template('validateDTD.html', res=res)
    return render_template('validateDTD.html',res=res)


@app.route('/xmltojson', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        res=""
        file = request.files['file']

        _, file_extension_xml = os.path.splitext(file.filename)
        if file and file_extension_xml == ".xml":
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            with open("static/"+file.filename) as xml_file:
                data_dict = xmltodict.parse(xml_file.read())

                json_data = json.dumps(data_dict, indent=4)
                f = open("jsonfile.json", "w")
                f.write(json_data)
                f.close() 
                return send_file("jsonfile.json",as_attachment=True)
        else:
            error = "Your file is not a .xml File, Retry again !"
            return render_template('xmltojson.html',error=error)
    return render_template('xmltojson.html')

if __name__ == '__main__':
    app.run(debug=True)
