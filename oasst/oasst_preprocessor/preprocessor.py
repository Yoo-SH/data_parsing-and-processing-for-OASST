import argparse
import parallel_processing as filtering
import os
import platform
import csv_preprocessor
import file_encoding_data
import qa_separator
import logging
from json_preprocessor import json_input_preprocessor, json_output_preprocessor
import under_sampling as sampling
import deduplicate as deduplicator


def direct_path_filter_file_link(filter_path):
    """
    입력 파일 경로를 확인하고, 필요 시 경로 형식을 조정합니다.

    Args:
        input_path (str): 입력 파일의 디렉토리 경로.

    Returns:
        str: 조정된 입력 파일 경로.
    """

    if os.path.isabs(filter_path) and platform.system() == "Windows":  # 상대경로가 아니라면
        print("filter_path가 절대경로 입니다. filter_path: " + str(filter_path))
        filter_path += '\\'
    else:
        filter_path += '/'

    print("필터 파일 입력 경로 확인:", filter_path)
    return filter_path


def direct_path_input_file_link(input_path):
    """
    입력 파일 경로를 확인하고, 필요 시 경로 형식을 조정합니다.

    Args:
        input_path (str): 입력 파일의 디렉토리 경로.

    Returns:
        str: 조정된 입력 파일 경로.
    """

    if os.path.isabs(input_path) and platform.system() == "Windows":  # 상대경로가 아니라면
        print("input_path가 절대경로 입니다. input_path: " + str(input_path))
        input_path += '\\'
    else:
        input_path += '/'

    print("인풋 파일 입력 경로 확인:", input_path)
    return input_path


def direct_path_output_file_link(output_path):
    """
    출력 파일 경로를 확인하고, 필요 시 경로 형식을 조정합니다.

    Args:
        output_path (str): 출력 파일의 디렉토리 경로.

    Returns:
        str: 조정된 출력 파일 경로.
    """

    if os.path.isabs(output_path) and platform.system() == "Windows":  # 상대경로가 아니라면
        print("output_path가 절대경로 입니다. output_path: " + str(output_path))
        output_path += '\\'
    else:
        output_path += '/'

    print("아웃풋 파일 출력 경로 확인:", output_path)
    return output_path


def check_link_rule(
    input_path, input_file_name, input_extention, output_file_name, output_extention, filter_path, filter_name, filter_extention, undersample_ratio
):
    """
    입력 및 출력 파일의 존재 여부와 유효성을 확인합니다.

    Args:
        input_path (str): 입력 파일의 디렉토리 경로.
        input_file_name (str): 입력 파일의 이름.
        output_file_name (str): 출력 파일의 이름 (선택 사항).
        filter_path (str): 필터 파일의 디렉토리 경로.
        filter_name (str): 필터 파일의 이름.
        args (argparse.Namespace): 명령줄 인수 파서 객체.

    Raises:
        SystemExit: 파일이 존재하지 않거나 필수 파일 이름이 주어지지 않은 경우 프로그램을 종료합니다.
    """

    if undersample_ratio < 1.0:
        print("Error: under sample ratio는 1.0 이상이어야 합니다.")
        exit(0)

    if not input_file_name:
        print("Error: 파일 이름을 입력해야 합니다.")
        exit(0)

    if not filter_name:
        print("Error: 필터 파일 이름을 입력해야 합니다.")
        exit(0)

    # XML 파일 존재 여부 확인
    if not os.path.exists(input_path + input_file_name):  # 입력 파일이 존재하지 않으면 프로그램 종료
        print(f"입력 파일이 존재하지 않습니다:{input_file_name}")
        exit(0)

    if filter_extention not in ('.csv', '.xlsx'):
        print(f"지원하지 않는 확장자 파일입니다. 다른 파일을 입력해주세요.{filter_extention}")
        exit(0)

    if not os.path.exists(filter_path + filter_name):  # 필터 파일이 존재하지 않으면 프로그램 종료
        print(f"필터 파일이 존재하지 않습니다:{filter_name}")
        exit(0)

    if input_extention not in ('.xlsx', '.csv', '.json', '.jsonl', '.parquet', '.feather') or output_extention not in (
        '.xlsx',
        '.csv',
        '.json',
        '.jsonl',
        '.parquet',
        '.feather',
    ):
        print(f"지원하지 않는 확장자 파일입니다. 다른 파일을 입력해주세요: {input_extention} or {output_extention}")
        exit(0)

    print("입력 파일 확인", input_file_name)
    print("출력 파일 확인", output_file_name)
    print("필터 파일 확인", filter_name)


def input_file_preprocess(input_file, input_extention, output_extention):
    """
    다른 파일 형식으로 처리하기 변환 및 전처리하기전에 입력 파일을 전처리 하는 함수입니다.

    Args:
        input_file (_type_): _description_
        input_type (_type_): _description_
    """

    # 파일 인코딩 확인 및  GLOBAL 인코딩값 설정.
    if input_extention == '.csv' or input_extention == '.json':
        file_encoding_data.get_encoding(input_file)
    else:
        file_encoding_data.GLOBAL_ENCODING_UNIFICATION = 'utf-8'

    if (output_extention == '.json' or input_extention == '.json') and file_encoding_data.GLOBAL_ENCODING_UNIFICATION != 'utf-8':
        logging.info("json 파일이용시, utf-8 형식으로만 지정해야합니다.")
        exit(0)

    # Preprocess CSV files
    if input_extention == '.csv':  # 일단은 csv(콤마)로 구분된 파일만 처리하도록 함, 나중에 tab으로 구분된 파일도 처리할 수 있도록 수정 필요
        csv_preprocessor.process_csv_comma(input_file)
    elif input_extention == '.csv':
        csv_preprocessor.process_csv_tab(input_file)

    if input_extention == '.json':
        json_input_preprocessor.convert_tree_to_flat(input_file)

    # 네이버 카페의 경우 QA분류 전처리를 시작함.
    separation_words = ['A.', '답변']
    if qa_separator.canQAseparated(input_file, input_extention, separation_words):
        qa_separator.preprocess_excel_file(input_file, separation_words)
    elif input_file.split('_')[1] == 'cafe' and input_extention != 'excel':
        print.info("cafe 파일을 QA분류 작업을 처리하기 위해서는 xlsx 파일 형식이 필요합니다. QA분류 작업을 건너 뜁니다.")


def output_file_preprocess(input_file, input_extention, output_file, output_extention):

    if input_extention == '.json':
        json_output_preprocessor.convert_flat_to_tree(input_file)

    if output_extention == '.json':
        json_output_preprocessor.convert_flat_to_tree(output_file)


def main():
    """
    메인 함수는 파일 형식에 따라 파일을 처리하고 출력 파일을 생성합니다.

    명령줄 인수를 통해 입력, 출력, 필터 파일의 경로와 파일 형식을 지정할 수 있습니다.
    """

    parser = argparse.ArgumentParser(description='Process files with various formats.')
    parser.add_argument('-input', required=True, help='input 경로와 파일 이름 (예: ./inputfile_name)')
    parser.add_argument('-output', required=True, help='output 경로와 파일 이름 (예: ./outputfile_name)')
    parser.add_argument('-filter_region', required=True, help='filter 경로와 파일 이름 (예: ./filterfile_name)')
    parser.add_argument('-input_format', required=True, help='oasst or text')
    parser.add_argument('-undersample', type=float, required=True, help='input over 1.0')

    args = parser.parse_args()

    input_path, input_file_name = os.path.split(args.input)  # 경로와 파일이름을 분리함
    input_extention = os.path.splitext(input_file_name)[1]  # 파일 확장자를 분리함

    output_path, output_file_name = os.path.split(args.output)  # 경로와 파일이름을 분리함
    output_extention = os.path.splitext(output_file_name)[1]  # 파일 확장자를 분리함

    filter_path, filter_file_name = os.path.split(args.filter_region)  # 경로와 파일이름을 분리함
    filter_extention = os.path.splitext(filter_file_name)[1]  # 파일 확장자를 분리함

    print("필터 파일 경로:", filter_path)
    print("필터 파일 이름:", filter_file_name)
    print("필터 파일 확장자:", filter_extention)

    input_path = direct_path_input_file_link(input_path)  # 경로 형식을 조정함  (상대경로나 절대경로인 경우에 따라 다름)
    output_path = direct_path_output_file_link(output_path)  # 경로 형식을 조정함  (상대경로나 절대경로인 경우에 따라 다름)
    filter_path = direct_path_filter_file_link(filter_path)  # 경로 형식을 조정함  (상대경로나 절대경로인 경우에 따라 다름)

    if not output_file_name:  # output file명을 입력하지 않으면, _decompress이름이 붙은 파일이 생성.
        output_file_name = input_file_name + '_decompress' + output_extention

    # 경로규칙 및 파일 존재 유무 확인
    check_link_rule(
        input_path, input_file_name, input_extention, output_file_name, output_extention, filter_path, filter_file_name, filter_extention, args.undersample
    )  # 경로와 파일이름을 확인함

    temp_file = args.input + '.tmp'

    # 파일 전처리(인코딩, json flatting, QA분류)
    input_file_preprocess(temp_file, input_extention, output_extention)

    # deduplicate
    deduplicator.remove_duplicate_prompters(temp_file)

    # Under sampling
    sampling.under_sampling(temp_file, args.undersample)

    # filtering data
    filtering.preprocess_data(temp_file, input_extention, args.output, output_extention, args.filter_region, filter_extention, os.cpu_count())

    # 파일 후처리(json tree 복원)
    output_file_preprocess(temp_file, input_extention, args.output, output_extention)

    os.remove(temp_file)


if __name__ == "__main__":
    main()
