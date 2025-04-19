
from funcs import complete_reports


def main(enter=input()):
    report = complete_reports(enter)
    total_requests = report[0]
    handler_data = report[1]

    header = f"""
Total requests: {total_requests}

HANDLER         DEBUG  INFO   WARNING ERROR  CRITICAL
-----------------------------------------------------"""

    content = ""
    for handler in sorted(handler_data):
        data = handler_data[handler]
        content += f"""{handler:<12}{data["DEBUG"]:<7}{data["INFO"]:<7}{data["WARNING"]:<7}{data["ERROR"]:<7}{data["CRITICAL"]}\n"""

    print(header)
    print(content)


if __name__ == "__main__":
    main()



