import json
import re
import os

# ファイルパスの取得
base = os.path.dirname(os.path.abspath(__file__))

# 図鑑番号抽出用の関数
def extract_leading_numbers(input_str):
    pattern = r'^\d{3,4}'
    match = re.match(pattern, input_str)
    if match:
        return match.group()
    else:
        return None
    
# 種族値抽出用の関数
def extract_numbers(input_str):
    pattern = r'(\d+\.\d+\.\d+\.\d+\.\d+\.\d+)'
    match = re.search(pattern, input_str)
    if match:
        numbers_str = match.group(1)
        numbers_list = [int(num) for num in numbers_str.split('.')]
        return numbers_list
    else:
        return None

# 特性の後ろからカッコを除く関数
def remove_brackets(input_str):
    output_str = input_str[:-4]
    return output_str

# 角括弧に囲まれた半角英数字を消す関数
def remove_bracketed_alphanumeric(input_str):
    pattern = r'\[[A-Za-z0-9]+\]'
    return re.sub(pattern, '', input_str)

# 元データの入ってるテキストファイル
DataFile = open(base + '\\Pokemon_Info.txt', 'r', encoding='UTF-8')

# どうやってポケモン一種類ごとのデータに分けるか考える
# "====="が出てきた回数で判断すればよい

lines = DataFile.readlines()
lines_strip = [line.strip() for line in lines]

DataFile.close()
# "====="が含まれる行番号を抽出
separators_raw = [i for i, line in enumerate(lines_strip) if '=====' in line]

# 奇数番目から始まり奇数番目で終わるため、separators の0, 2, 4, 6, ... 要素だけにする
separators = []
for i in range(int(len(separators_raw) / 2)):
    separators.append(separators_raw[2 * i])

# テキストデータの内容をポケモンごとに分けたもの
pokedata_txt_list = []

# JSON形式データのリスト
pokedata_JSON_list = []

for i in range(len(separators)):
    # 元データに入ってる最後のポケモンに対する処理
    if i == len(separators) - 1:
        pokedata_txt = lines_strip[separators[i]:len(lines_strip) + 1]

    else:
        pokedata_txt = lines_strip[separators[i]:separators[i + 1]]
    pokedata_txt_list.append(pokedata_txt)

# ポケモン1種類ごとのデータを整形してJSONにする
for pokedata_txt in pokedata_txt_list:
    pokedata_JSON = {}

    # 図鑑番号(厳密には違うっぽい)を抽出する
    DexNo = int(extract_leading_numbers(pokedata_txt[1]))
    pokedata_JSON['DexNo'] = DexNo

    # 種族値を抽出する
    BaseStat = extract_numbers(pokedata_txt[3])
    pokedata_JSON['BaseStat'] = BaseStat

    # 特性を抽出する
    Abilities_raw = pokedata_txt[7].removeprefix("Abilities: ").split(" | ")
    Abilities = [remove_brackets(Ability) for Ability in Abilities_raw]
    pokedata_JSON['Abilities'] = Abilities

    # タイプを抽出する
    PokeType = pokedata_txt[8].removeprefix('Type: ').split(" / ")
    pokedata_JSON['PokeType'] = PokeType

    # 経験値タイプを抽出する
    ExpType = pokedata_txt[9].removeprefix('EXP Group: ')
    pokedata_JSON['ExpType'] = ExpType

    # タマゴグループを抽出する
    EggGroup = pokedata_txt[10].removeprefix('Egg Group: ').split(" / ")
    pokedata_JSON['EggGroup'] = EggGroup

    # 体重を抽出する
    Weight = float(pokedata_txt[11].split(', ')[1].removeprefix('Weight: ').removesuffix('kg'))
    pokedata_JSON['Weight'] = Weight

    # 進化先と覚える技を抽出する
    Moves_list = []
    Evolutions = []
    for line in pokedata_txt[12:]:
        if len(line) == 0:
            continue
        if line[0] == '-':
            # 技の抽出
            MoveName = remove_bracketed_alphanumeric(line).removeprefix('-').strip()
            Moves_list.append(MoveName)
        elif 'Evolves into ' in line:
            # 進化先の抽出
            EvolutionName = line[:line.find(' @ ')].removeprefix('Evolves into ')
            Evolutions.append(EvolutionName)

    # 集合に変換してからリストに戻して、重複している技を消す
    Moves_set = set(Moves_list)
    Moves_list = list(Moves_set)
    pokedata_JSON['Moves'] = Moves_list
    pokedata_JSON['Evolutions'] = Evolutions
    pokedata_JSON_list.append(pokedata_JSON)

output_file = open(base + '\\output.json', 'w', encoding='UTF-8')
json.dump(pokedata_JSON_list, output_file, indent=4, ensure_ascii=False)
output_file.close()