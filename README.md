# Tello drone app
Ryze Tech社のドローン [Tello](https://www.ryzerobotics.com/jp/tello) を制御するWebアプリです。

## 概要

ドローンの離陸、着陸、移動、回転などの操作が行えます。
制御方法には以下の2つがあります。

1. WebUIでの操作

WebUIのボタンでドローン操作ができます。

![WebUI](https://github.com/user-attachments/assets/a445f07e-08e9-49c8-8d39-6d179c3370c4)


2. AI画像解析での操作 (実装中)
ドローンカメラで撮影した映像から人物の動きを骨格検知で判定しドローンを動かせます。

例) 人が両手を挙げる ➡ ドローン上昇
    人が右手を挙げる ➡ ドローン右に移動 など。


