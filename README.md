* 情報は少しずつ追加予定
* プログラムは現状ほぼ未完成


センシング部隊
============================================================
IoTデバイスでの大規模センシングを行うための基盤

グループごとでのデータの集計やセンシング設定の変更を柔軟にできることを目的とするもの


### 全体の概要図
![arch-fig](docs/fig/arch.png)

プログラムについて
============================================================
### 外部ライブラリ
* flask
* requests

### 起動時パラメータ
Private, Sergeantは自身のAPI受付ポートと上官のIP/ポートを指定する必要がある

例:
```
$ python3 private.py 5001 localhost 5000  
$ python3 sergeant.py 5000 localhost 5100
```

### サンプル起動
0. private, sergeantを上記の例のパラメータで、captainはそのまま起動する
  - 階層的に上位のものから起動する; captain -> sergeant -> private
0. private, sergeantは起動直後に上官への入隊を自動的に行う
0. それぞれのアクタのAPIを使って動作を見る；下記参照

### APIテスト用コンフィグファイル
test/下にcurlコマンドで使えるconfファイルがあり、それぞれAPIのテストデータなどが入っている
```
$ curl --config test/pvt_order.conf
```
* sgt_cache.conf / cpt_cache.conf
  - Sergeant / Captainが受信したデータを表示する
* pvt_order.conf
  - Privateにセンシング命令を出すAPI
  - ランダム値を2秒ごと、ゼロ値を5秒ごとに送信する設定
* sgt_job.conf
  - Sergeantにレポート命令を出すAPI
  - Privateから受信して貯めたデータを8秒ごとに送信する設定

