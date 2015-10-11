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
outgdb="test3.gdb"

#計算結果を格納するファイルのファイル名を指定する
outfile="final"

try:

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
    
    
    #小地域データのリストをSCFilesに取得
    #"h22*"のファイルの一覧を取得する
    fcs=arcpy.ListFeatureClasses("h22*")
    
    
    for fc in fcs:
        
        #ファイルジオデータベース内の小地域データのファイル名
        base, ext=os.path.splitext(fc)
        shoufilename=outgdb+"\\" + base

        
        # 小地域データをファイルジオデータベースへコピー
        arcpy.FeatureClassToFeatureClass_conversion(fc, outgdb, base)

        # 小地域データに人口密度を格納するフィールド"dens"を追加
        arcpy.AddField_management(shoufilename, "dens", "DOUBLE")
        
        # フィールド演算を用いて人口密度を計算し，densに格納する
        arcpy.CalculateField_management(shoufilename, "dens","!JINKO!/!AREA!", "PYTHON")
        
        # 学区データと小地域データをインターセクトしてintersectとして保存する
        arcpy.Intersect_analysis([outgdb+"\A27_JGD2000", shoufilename], shoufilename + "_intersect")
        
        # 区画ごとの人口を入れるフィールドを追加
        arcpy.AddField_management(shoufilename+"_intersect", "n_area", "DOUBLE")
        
        # フィールド演算を用いて区画ごとの人口を計算
        # shape/areaは各シェープの面積を表すプロパティ（あえて面積を計算する必要はない）
        arcpy.CalculateField_management(shoufilename+"_intersect", "n_area", "!shape.area!*!dens!", "PYTHON")
        
        #ディゾルブして人口の合計を計算する
        arcpy.Dissolve_management(shoufilename+"_intersect", shoufilename+"_dissolve", "FID_A27_JGD2000", [["n_area", "SUM"],["A27_006", "LAST"],["A27_007", "LAST"],["A27_008", "LAST"]])

except:
    print arcpy.GetMessages()
print r"finish"