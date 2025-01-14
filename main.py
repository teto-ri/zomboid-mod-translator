from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import os
from openai import OpenAI

client = OpenAI(
    api_key = "",
)

def translate_line(line, source_lang="English", target_lang="Korean"):
    """
    GPT API를 사용하여 한 줄 번역.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": f"You are a game dialogue translator that translates {source_lang} to {target_lang}. The way you speak is like a zombie apocalypse survivor."},
                {"role": "user", "content": f"Translate the following line into {target_lang}: {line}"}
            ]
        )
        return response.choices[0].message.content.replace('"',"")
    except Exception as e:
        print(f"Error translating line: {line.strip()} - {e}")
        return line  # 오류 발생 시 원본 문장 반환

def process_line(line):
    """
    한 줄 처리 - 번역이 필요한 라인만 번역.
    """
    if ('UI_DM' in line) and ('--' not in line):  # 번역 대상이 되는 라인만 처리
        key, value = line.split('=', 1)
        value = value.strip().replace('"',"")[:-1]  # 불필요한 공백 및 따옴표 제거
        translated_value = translate_line(value)
        return f'{key} = "{translated_value}",\n'
    else:
        return line  # 번역이 필요 없는 라인 그대로 반환

def translate_file_with_parallel_processing(input_file, output_file, max_workers=5):
    """
    파일의 각 줄을 병렬로 번역하고 진행률을 출력하며 결과를 저장.
    """
    with open(input_file, 'r', encoding='utf-8') as infile:
        lines = infile.readlines()

    # lines = lines[:10]
    # 병렬 번역 처리
    translated_lines = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(process_line, line): line for line in lines}
        for future in tqdm(as_completed(futures), total=len(futures), desc="Translating"):
            translated_lines.append(future.result())

    # 원래 순서를 유지하기 위해 정렬
    translated_lines = [f.result() for f in sorted(futures.keys(), key=lambda x: lines.index(futures[x]))]

    # 결과 저장
    with open(output_file, 'w', encoding='utf-8') as outfile:
        outfile.writelines(translated_lines)

    print(f"Translated file saved to {output_file}")

if __name__ == "__main__":
    # 파일 경로 설정
    input_file_path = "UI_EN.txt"  # 입력 파일 경로
    output_file_path = "UI_KO.txt"  # 번역 결과 저장 파일 경로

    # 번역 함수 실행
    translate_file_with_parallel_processing(input_file_path, output_file_path, max_workers=10)