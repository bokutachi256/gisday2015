# -*- coding: utf-8 -*-
"""
GIS Day in 東京 2015
Dコースサンプルプログラム

国土数値情報小学校区データと
国勢調査小地域データから
面積按分で小学校区の人口を推定する

arcpy_test05.py

0: 初期バージョン，ツールボックスを羅列したもの
1: try exceptでかこんだやつ
2: ワークスペースにあるすべての小地域データに対して実行するバージョン
    ListFeatureClassesで対象ファイルのリストを取得し，
    forループで実行するバージョン
3: 不要データを削除する機能を追加
4: データをマージする機能を追加
5: ツールボックスから実行できるバージョン
    ワークスペース名と出力先のジオデータベースをツールボックスから取得する
"""

# arcpyの読み込み
import sys
import os
import arcpy
from arcpy import env

# ワークスペースの指定
# 引数からワークスペース名を取得する
env.workspace = arcpy.GetParameterAsText(0)

# データを格納するファイルジオデータベースの名前を引数から取得する
outgdb=arcpy.GetParameterAsText(1)

try:

    # データを格納するファイルジオデータベースの作成
    # GetParameterAsText(1)で指定されているジオデータベースはすでに作成されているため，
    # ここではジオデータベースを作成しない
    # arcpy.CreateFileGDB_management(".", outgdb)

    # 投影法を設定する対象のファイル
    # 国土数値情報の小学校区データ
    infc=r"A27-10_13-g_SchoolDistrict.shp"
    
    # 空間リファレンスを取得
    # 4612はGCS_JGD2000のWKID
    sr=arcpy.SpatialReference(4612)
    
    # 投影法の定義を実行する
    # 小学校区データにGCS_JGD2000を付与
    arcpy.DefineProjection_management(infc,sr)
    
    # 投影変換のためのリファレンスを指定する
    # 2451はJGD2000 zone9のWKID
    out_proj=arcpy.SpatialReference(2451)
    # 投影変換を行う．
    arcpy.Project_management("A27-10_13-g_SchoolDistrict.shp", outgdb + "\A27_JGD2000", out_proj)
    
    # 小地域データのリストをfcsに取得
    # "h22*"のファイルの一覧を取得する
    fcs=arcpy.ListFeatureClasses("h22*")
    
    # ワークスペースにある小地域データすべてについて面積按分を実行する
    for fc in fcs:
        
        # ファイルジオデータベース内の小地域データのファイル名をファイル名と拡張子で分割する
        # baseにファイル名，extに拡張子が入る
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
        # shape.areaは各シェープの面積を表すプロパティ（あえて面積を計算する必要はない）
        arcpy.CalculateField_management(shoufilename+"_intersect", "n_area", "!shape.area!*!dens!", "PYTHON")
        
        # ディゾルブして人口の合計を計算する
        arcpy.Dissolve_management(shoufilename+"_intersect", shoufilename+"_dissolve", "FID_A27_JGD2000", [["n_area", "SUM"],["A27_006", "LAST"],["A27_007", "LAST"],["A27_008", "LAST"]])
        
        # いらないデータを削除する
        arcpy.Delete_management(shoufilename+"_intersect")
        arcpy.Delete_management(shoufilename)

    # 出力先のジオデータベースに入る
    env.workspace=outgdb
    # ジオデータベス内のdissolveファイルのリストを取得する
    fcs=arcpy.ListFeatureClasses("h22ka*")

    # fcsに対してマージを行う
    arcpy.Merge_management(fcs, outgdb+"\mergedata")
    
except:
    print arcpy.GetMessages()

    # ツールボックスから動かす場合には終了時のメッセージは不要
    # print r"finish"
