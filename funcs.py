from typing import List

def remove_None_string(string_lst:list[str]):
    return [ s for s in string_lst if s!='']

def get_endpoint(line:str):
    line_lst=line.split(" ")
    line_lst=remove_None_string(line_lst)
    for word in line_lst:
      if "/" in word:
         return word
    return None
def get_logging_level(line:str):
    line_lst=line.split(" ")
    line_lst=remove_None_string(line_lst)
    for index_word in range(len(line_lst)): 
     if index_word!=len(line_lst)-1:
      if "django." in line_lst[index_word+1]:
         return line_lst[index_word]
    return None


def handler(file_paths: List[str]):

    total_requests=0
    endpoint_dict={}
    log_lines=[]
    for file_path in file_paths:
        if not file_path:
           continue
        try: 
         with open(file_path,"rt",encoding="utf-8") as file:
             while(line:=file.readline()):
                log_lines.append(line)       
        except FileNotFoundError:
            raise Exception(f"File {file_path} does not exist , please enter the path correctly")
        for line in log_lines:
            if "django.request" in line:
                    total_requests+=1
                    try: 
                     endpoint_dict[get_endpoint(line)][get_logging_level(line)]+=1
                    except KeyError:
                    #logs/app1.log --report handler
                      endpoint_dict.setdefault(get_endpoint(line),{"DEBUG":0,"INFO":0,"WARNING":0,"ERROR":0,"CRITICAL":0})
    
    return [total_requests,endpoint_dict]


def report(report_name,files):
  match(report_name):
    case "handler":
      return handler(files)
    case _:

        #raise Exception("this method does not exist")
        return []


def complete_reports(files_paths:str):
   
   files=files_paths.split(' ')
   files=remove_None_string(files)
   pattern="--report"
   
   if pattern in files:
     report_name=files[files.index(pattern)+1]
     files.remove(pattern)
     files.remove(report_name)
     
     return report(report_name,files)