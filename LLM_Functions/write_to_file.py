print("這是一個程式讓你可以寫入一些內容到文件中")
file_path = input("請輸入檔案路徑(含副檔名):")
with open(file_path, "w", encoding="utf-8") as f:
    f.write(input("請輸入要寫入的內容："))
