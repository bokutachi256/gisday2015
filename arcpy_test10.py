#coding:utf-8
"""
gisday2015 テストプログラム
ファイルジオデータベース内のデータを取得する


"""
# arcpyの読み込み
import sys
import os
import arcpy
from arcpy import env

env.workspace = os.path.abspath(os.path.dirname(sys.argv[0]))
env.workspace="test2.gdb"

finalFS= arcpy.Describe("final")
print finalFS.ShapeType
flds= finalFS.Fields
for fld in flds:
    print fld.name
    print fld.type
    print fld.length
