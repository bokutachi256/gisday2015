#coding:utf-8
"""
GIS Day in 東京 2015
Dコースサンプルプログラム

国土数値情報小学校区データと
国勢調査小地域データから
面積按分で小学校区の人口を推定する
"""

# arcpyの読み込み
import sys
import os
import arcpy
from arcpy import env

#ワークスペースの指定
#できればワークスペースのパス名は以下で取得する
#os.path.abspath(os.path.dirname(sys.argv[0]))
#すなわちPythonスクリプトの絶対パス
#env.workspace="C:\Users\Dee\Documents\Dropbox\workspace\gisday2015"
env.workspace = os.path.abspath(os.path.dirname(sys.argv[0]))

#データを格納するファイルジオデータベースの名前を指定する
outgdb="test2.gdb"

#計算結果を格納するファイルのファイル名を指定する
outfile="final"

# データを格納するファイルジオデータベースの作成
arcpy.CreateFileGDB_management(".", outgdb)

# 投影法を設定する対象のファイル
# 国土数値情報の小学校区データ
infc=r"A27-10_13-g_SchoolDistrict.shp"

# 空間リファレンスを取得
#4612はGCS_JGD2000のWKID
sr=arcpy.SpatialReference(4612)

# 投影法の定義を実行する
# 小学校区データにGCS_JGD2000を付与
arcpy.DefineProjection_management(infc,sr)

#投影変換のためのリファレンスを指定する
#2451はJGD2000 zone9のWKID
out_proj=arcpy.SpatialReference(2451)
#投影変換を行う．
arcpy.Project_management("A27-10_13-g_SchoolDistrict.shp", outgdb + "\A27_JGD2000", out_proj)

# 小地域データをファイルジオデータベースへコピー
#arcpy.FeatureClassToFeatureClass_conversion("h22ka13224", "test.gdb", "h22ka13224")
arcpy.FeatureClassToFeatureClass_conversion("h22ka13224.shp", outgdb, "h22ka13224")

# 小地域データに人口密度を格納するフィールド"dens"を追加
arcpy.AddField_management(outgdb+"\h22ka13224", "dens", "DOUBLE")

# フィールド演算を用いて人口密度を計算し，densに格納する
arcpy.CalculateField_management(outgdb + "\h22ka13224", "dens","!JINKO!/!AREA!", "PYTHON")

# 学区データと小地域データをインターセクトしてintersectとして保存する
arcpy.Intersect_analysis([outgdb+"\A27_JGD2000", outgdb+"\h22ka13224"], outgdb+"\intersect")

# 区画ごとの人口を入れるフィールドを追加
arcpy.AddField_management(outgdb+"\intersect", "n_area", "DOUBLE")

# フィールド演算を用いて区画ごとの人口を計算
# shape/areaは各シェープの面積を表すプロパティ（あえて面積を計算する必要はない）
arcpy.CalculateField_management(outgdb+"\intersect", "n_area", "!shape.area!*!dens!", "PYTHON")

#ディゾルブして人口の合計を計算する
arcpy.Dissolve_management(outgdb+"\intersect", outgdb+"\\"+outfile, "FID_A27_JGD2000", [["n_area", "SUM"],["A27_006", "LAST"],["A27_007", "LAST"],["A27_008", "LAST"]])

