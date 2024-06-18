import os
import win32print
import subprocess
from flask import Flask, request, render_template_string
import win32api
import time


app = Flask(__name__)
UPLOAD_FOLDER = 'D:\\uploads\\' ##设置上传目录
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xls', 'xlsx'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def set_default_printer(printer_name):
    try:
        win32print.SetDefaultPrinter(printer_name)
        return True
    except Exception as e:
        print(f"设置默认打印机失败: {str(e)}")
        return False

def print_file(filepath, printer_name):
    try:
        print(f"正在打印的打印机: {printer_name}")

        # 设置默认打印机
        if not set_default_printer(printer_name):
            raise ValueError("指定的打印机未找到或无法设置为默认打印机。")

        # 打印文件
        file_extension = filepath.rsplit('.', 1)[1].lower()

        if file_extension in {'txt', 'pdf', 'doc', 'docx', 'xls', 'xlsx'}:
            # 使用 win32api 打印文件
            win32api.ShellExecute(0, "print", filepath, None, ".", 0)
        elif file_extension in {'png', 'jpg', 'jpeg', 'gif'}:
            # 使用 Windows 照片查看器打印图像文件
            subprocess.run(['rundll32', 'C:\\WINDOWS\\System32\\shimgvw.dll,ImageView_PrintTo', filepath, printer_name], check=True)
        else:
            raise ValueError("不支持的文件类型。")

        print("文件打印成功")
        
        # 删除文件
        #time.sleep(5)
        #os.remove(filepath)
        #print("文件已删除")
        return "文件打印成功"
    except Exception as e:
        print(f"发生错误: {str(e)}")
        return f"打印文件失败: {str(e)}"


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    with open(os.path.join(app.static_folder, 'index.html'), 'r', encoding='utf-8') as file:
        html = file.read()

    message = None
    message_class = None

    if request.method == 'POST':
        if 'file' not in request.files:
            message = '没有文件部分'
            message_class = 'error'
        else:
            file = request.files['file']
            if file.filename == '':
                message = '未选择文件'
                message_class = 'error'
            elif file and allowed_file(file.filename):
                filename = file.filename
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                file.save(filepath)
                printer_name = request.form.get('printer')
                try:
                    message = print_file(filepath, printer_name)
                    message_class = 'success' if '成功' in message else 'error'
                except Exception as e:
                    message = f'打印文件失败: {str(e)}'
                    message_class = 'error'

        return render_template_string(html, message=message, message_class=message_class, printers=get_printers())

    return render_template_string(html, printers=get_printers())


def get_printers():
    return [printer[2] for printer in win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)]


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)
