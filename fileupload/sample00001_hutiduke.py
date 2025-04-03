import cv2
import numpy as np
import argparse
import os
import glob
import shutil
from pathlib import Path
import zipfile

def add_outline(image_path, output_path, outline_size=8, outline_color=(255, 255, 255, 255)):
    """
    透過PNG画像に外側の輪郭（アウトライン）を追加する関数
    
    Parameters:
    -----------
    image_path : str
        入力画像のパス
    output_path : str
        出力画像のパス
    outline_size : int
        輪郭の太さ（ピクセル）
    outline_color : tuple
        輪郭の色 (B, G, R, A)
    """
    # 画像を読み込む
    img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    
    if img is None:
        print(f"エラー: 画像 {image_path} を読み込めませんでした")
        return False
    
    # アルファチャンネルがない場合は追加
    if img.shape[2] == 3:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)
    
    # アルファチャンネルを抽出
    alpha = img[:, :, 3]
    
    # 膨張カーネルを作成（輪郭の太さを制御）
    kernel = np.ones((outline_size, outline_size), np.uint8)
    
    # アルファチャンネルを膨張させて、外側の輪郭用のマスクを作成
    dilated = cv2.dilate(alpha, kernel, iterations=1)
    
    # 元のアルファを差し引いて外側の輪郭のみのマスクを取得
    outline_mask = dilated - alpha
    
    # 輪郭用の画像を作成
    outline_img = np.zeros_like(img)
    
    # OpenCVでの色の順序はB,G,R,Aなので注意
    outline_img[:, :] = outline_color
    
    # 輪郭のアルファチャンネルを設定
    outline_img[:, :, 3] = outline_mask
    
    # 元の画像をパディングして大きくする（輪郭を外側に追加するため）
    h, w = img.shape[:2]
    padded_img = np.zeros((h + outline_size*2, w + outline_size*2, 4), dtype=np.uint8)
    padded_outline = np.zeros((h + outline_size*2, w + outline_size*2, 4), dtype=np.uint8)
    
    # 中央に元の画像を配置
    padded_img[outline_size:outline_size+h, outline_size:outline_size+w] = img
    
    # 輪郭を配置
    padded_outline[outline_size:outline_size+h, outline_size:outline_size+w] = outline_img
    
    # 輪郭と元の画像を合成
    # まず輪郭を配置し、その上に元の画像を重ねる
    result = padded_outline.copy()
    mask = padded_img[:, :, 3:4] / 255.0
    result = result * (1.0 - mask) + padded_img * mask
    
    # 結果を保存
    cv2.imwrite(output_path, result.astype(np.uint8))
    print(f"アウトラインを追加した画像を {output_path} に保存しました")
    return True

def process_directory(input_dir, output_dir, outline_size=8, outline_color=(255, 255, 255, 255)):
    """
    ディレクトリ内のすべてのPNG画像を処理する
    """
    # 入力ディレクトリを作成（存在しない場合）
    os.makedirs(input_dir, exist_ok=True)
    # 出力ディレクトリを作成（存在しない場合）
    os.makedirs(output_dir, exist_ok=True)
    
    # 処理した画像のリストを保持する（HTML生成用）
    processed_images = []
    
    # 入力ディレクトリ内のすべてのPNGファイルを処理
    for image_path in glob.glob(os.path.join(input_dir, "*.png")):
        # 入力ファイル名
        filename = os.path.basename(image_path)
        # 出力ファイルパス
        output_path = os.path.join(output_dir, filename)
        
        # 画像処理を実行
        success = add_outline(image_path, output_path, outline_size, outline_color)
        
        if success:
            processed_images.append(filename)
    
    return processed_images

def create_zip_files(input_dir, output_dir):
    """
    入力および出力ディレクトリの画像をZIPファイルにまとめる
    """
    # 入力ディレクトリの内容をZIP化
    input_zip_path = 'original_images.zip'
    with zipfile.ZipFile(input_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file in glob.glob(os.path.join(input_dir, "*.png")):
            zipf.write(file, os.path.basename(file))
    
    # 出力ディレクトリの内容をZIP化
    output_zip_path = 'outlined_images.zip'
    with zipfile.ZipFile(output_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file in glob.glob(os.path.join(output_dir, "*.png")):
            zipf.write(file, os.path.basename(file))
    
    print(f"元画像のZIPファイルを {input_zip_path} に作成しました")
    print(f"処理後画像のZIPファイルを {output_zip_path} に作成しました")
    
    return input_zip_path, output_zip_path

def generate_html(processed_images, input_dir, output_dir, input_zip, output_zip):
    """
    処理前後の画像を比較するHTMLを生成する
    """
    html_content = """
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>画像比較ビューア</title>
    <style>
        body {
            font-family: 'Helvetica Neue', Arial, sans-serif;
            background-color: #1a1a1a;
            color: #f0f0f0;
            padding: 20px;
            margin: 0;
        }
        
        h1 {
            text-align: center;
            margin-bottom: 30px;
            font-weight: 300;
            letter-spacing: 1px;
            color: #ffffff;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .download-section {
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-bottom: 30px;
            padding: 20px;
            background-color: #111;
            border-radius: 8px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.5);
        }
        
        .download-btn {
            display: inline-block;
            padding: 12px 24px;
            background-color: #00bcd4;
            color: #fff;
            text-decoration: none;
            border-radius: 4px;
            font-weight: 500;
            transition: all 0.3s ease;
            border: none;
            cursor: pointer;
            font-size: 16px;
        }
        
        .download-btn:hover {
            background-color: #0097a7;
            transform: translateY(-2px);
            box-shadow: 0 5px 10px rgba(0, 0, 0, 0.2);
        }
        
        .download-btn.original {
            background-color: #7e57c2;
        }
        
        .download-btn.original:hover {
            background-color: #673ab7;
        }
        
        .image-comparison {
            display: flex;
            margin-bottom: 40px;
            background-color: #000;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.5);
        }
        
        .image-col {
            flex: 1;
            padding: 20px;
            text-align: center;
            border-right: 1px solid #333;
        }
        
        .image-col:last-child {
            border-right: none;
        }
        
        .image-col h3 {
            margin-top: 0;
            margin-bottom: 15px;
            font-weight: 400;
            color: #bbb;
        }
        
        img {
            max-width: 100%;
            height: auto;
            display: block;
            margin: 0 auto;
            background-color: #000;
        }
        
        .filename {
            font-family: monospace;
            color: #00bcd4;
            margin-top: 15px;
            font-size: 0.9rem;
        }
        
        .count-badge {
            display: inline-block;
            background-color: rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            padding: 5px 10px;
            font-size: 0.8rem;
            margin-left: 10px;
            vertical-align: middle;
        }
        
        @media (max-width: 768px) {
            .image-comparison {
                flex-direction: column;
            }
            
            .image-col {
                border-right: none;
                border-bottom: 1px solid #333;
            }
            
            .image-col:last-child {
                border-bottom: none;
            }
            
            .download-section {
                flex-direction: column;
                gap: 10px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>透過画像の輪郭比較 <span class="count-badge">全 """ + str(len(processed_images)) + """ 画像</span></h1>
        
        <div class="download-section">
            <a href=\"""" + input_zip + """\" class="download-btn original" download>元画像をまとめてダウンロード</a>
            <a href=\"""" + output_zip + """\" class="download-btn" download>輪郭追加画像をまとめてダウンロード</a>
        </div>
"""

    # 各画像の比較セクションを追加
    for filename in processed_images:
        input_path = os.path.join(input_dir, filename)
        output_path = os.path.join(output_dir, filename)
        
        # 相対パスに変換
        input_rel_path = os.path.relpath(input_path, os.path.dirname('index.html'))
        output_rel_path = os.path.relpath(output_path, os.path.dirname('index.html'))
        
        html_content += f"""
        <div class="image-comparison">
            <div class="image-col">
                <h3>元の画像</h3>
                <img src="{input_rel_path}" alt="元の画像">
                <div class="filename">{filename}</div>
            </div>
            <div class="image-col">
                <h3>輪郭追加後</h3>
                <img src="{output_rel_path}" alt="処理後の画像">
                <div class="filename">{filename}</div>
            </div>
        </div>
"""

    html_content += """
    </div>
    <script>
        // 画像の読み込み完了後に通知を表示
        window.addEventListener('load', function() {
            console.log('すべての画像が読み込まれました。');
        });
    </script>
</body>
</html>
"""

    # HTMLファイルを保存
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"比較用HTMLを index.html に生成しました。")

def main():
    parser = argparse.ArgumentParser(description='フォルダ内のすべての透過PNG画像に外側の輪郭を追加するツール')
    parser.add_argument('--input', default='input', help='入力画像が保存されているフォルダ（デフォルト: input）')
    parser.add_argument('--output', default='output', help='処理後画像を保存するフォルダ（デフォルト: output）')
    parser.add_argument('--size', type=int, default=8, help='輪郭の太さ（ピクセル）、デフォルト：8px')
    parser.add_argument('--color', default='255,255,255,255', help='輪郭の色（B,G,R,A形式）、デフォルト：255,255,255,255（白）')
    parser.add_argument('--html', action='store_true', help='処理後に比較用HTMLを生成する')
    
    args = parser.parse_args()
    
    # 色の文字列をタプルに変換
    color = tuple(map(int, args.color.split(',')))
    
    # ディレクトリ内のすべての画像を処理
    processed_images = process_directory(args.input, args.output, args.size, color)
    
    # 入力/出力画像をZIP化
    input_zip, output_zip = create_zip_files(args.input, args.output)
    
    # HTMLを生成（--htmlフラグが指定されているか、画像が処理された場合）
    if args.html or len(processed_images) > 0:
        generate_html(processed_images, args.input, args.output, input_zip, output_zip)

if __name__ == "__main__":
    main()
