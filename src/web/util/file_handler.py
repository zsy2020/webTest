"""
文件读写。YamlReader读取yaml文件，ExcelHandler读写excel。
"""
import os
import shutil
from datetime import datetime

import openpyxl
import yaml
from xlrd import open_workbook, xldate_as_tuple


def find_file(start_dir, file_name):
    doc_list = os.listdir(start_dir)
    for doc in doc_list:
        doc_path = os.path.join(start_dir, doc)
        if os.path.isdir(doc_path):
            result = find_file(doc_path, file_name)
            if result:
                return result
        else:
            if doc == file_name:
                return doc_path


def last_file(path):
    """找到最新的文件或文件夹"""
    # 列出目录下所有的文件
    doc_list = os.listdir(path)
    # 对文件修改时间进行升序排列
    doc_list.sort(key=lambda fn: os.path.getmtime(path + '\\' + fn))
    # 获取最新修改时间的文件
    filetime = datetime.fromtimestamp(os.path.getmtime(path + '\\' + doc_list[-1]))
    # 获取文件所在目录
    filepath = os.path.join(path, doc_list[-1])
    print("最新修改的文件(夹)：" + doc_list[-1])
    print("时间：" + filetime.strftime('%Y-%m-%d %H-%M-%S'))
    return filepath


def move_file(old_path, new_path):
    print(old_path)
    print(new_path)
    fileList = os.listdir(old_path)  # 列出该目录下的所有文件,listdir返回的文件列表是不包含路径的。
    print(fileList)
    for file in fileList:
        if file.startswith('__init__'):
            continue
        src = os.path.join(old_path, file)
        dst = os.path.join(new_path, file)
        print('src:', src)
        print('dst:', dst)
        shutil.move(src, dst)


def del_file(path):
    """删除指定文件夹的所有文件"""
    ls = os.listdir(path)
    for i in ls:
        if i.startswith('__init__'):
            continue
        c_path = os.path.join(path, i)
        if os.path.isdir(c_path):
            del_file(c_path)
        else:
            print('delete file:%s' % c_path)
            os.remove(c_path)


class YamlReader:
    def __init__(self, yamlf):
        if os.path.exists(yamlf):
            self.yamlf = yamlf
        else:
            raise FileNotFoundError('文件不存在！')
        self._data = None

    @property
    def data(self):
        # 如果是第一次调用data，读取yaml文档，否则直接返回之前保存的数据
        if not self._data:
            with open(self.yamlf, 'rb') as f:
                self._data = list(yaml.safe_load_all(f))  # load后是个generator，用list组织成列表
        return self._data


class SheetTypeError(Exception):
    pass


def formatDate(s, iRow):
    row_values = s.row_values(iRow)
    for iCol in range(s.ncols):
        # Python读Excel，返回的单元格内容的类型有5种：
        # ctype： 0 empty,1 string, 2 number, 3 date, 4 boolean, 5 error
        ctype = s.cell(iRow, iCol).ctype

        # ctype =3,为日期
        if ctype == 3:
            cell_value = s.cell_value(iRow, iCol)
            date = datetime(*xldate_as_tuple(cell_value, 0))
            cell_format = date.strftime('%Y-%m-%d')  # ('%Y/%m/%d %H:%M:%S')
            print(cell_value)
            print(cell_format)
            row_values[iCol] = cell_format
    return row_values


class ExcelHandler:
    """
    读取excel文件中的内容。返回list。

    如：
    excel中内容为：
    | A  | B  | C  |
    | A1 | B1 | C1 |
    | A2 | B2 | C2 |

    如果 print(ExcelReader(excel, title_line=True).data)，输出结果：
    [{A: A1, B: B1, C:C1}, {A:A2, B:B2, C:C2}]

    如果 print(ExcelReader(excel, title_line=False).data)，输出结果：
    [[A,B,C], [A1,B1,C1], [A2,B2,C2]]

    可以指定sheet，通过index或者name：
    ExcelReader(excel, sheet=2)
    ExcelReader(excel, sheet='BaiDuTest')
    """

    def __init__(self, path, sheet=0, title_line=False):
        if os.path.exists(path):
            self.excel = path
        else:
            raise FileNotFoundError('文件不存在！')
        self.sheet = sheet
        self.title_line = title_line
        self._data = list()

    @property
    def data(self):
        if not self._data:
            workbook = open_workbook(self.excel)
            if type(self.sheet) not in [int, str]:
                raise SheetTypeError('Please pass in <type int> or <type str>, not {0}'.format(type(self.sheet)))
            elif type(self.sheet) == int:
                s = workbook.sheet_by_index(self.sheet)
            else:
                s = workbook.sheet_by_name(self.sheet)

            if self.title_line:
                title = s.row_values(0)  # 首行为title
                for col in range(1, s.nrows):
                    # 依次遍历其余行，与首行组成dict，拼到self._data中
                    row_values = formatDate(s, col)
                    self._data.append(dict(zip(title, row_values)))
            else:
                for col in range(0, s.nrows):
                    # 遍历所有行，拼到self._data中
                    row_values = formatDate(s, col)
                    self._data.append(row_values)
        return self._data

    @data.setter
    def data(self, value):
        index = len(value)
        workbook = openpyxl.load_workbook(self.excel)
        sheet = workbook.active
        for i in range(0, index):
            sheet.append(value[i])
        workbook.save(self.excel)
