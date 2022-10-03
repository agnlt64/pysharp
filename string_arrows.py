def string_arrows(text: str, pos_start, pos_end):
    result = ""
    
    index_start = max(text.rfind("\n", 0, pos_start.index), 0)
    index_end = text.find("\n", index_start + 1)
    if index_end < 0:
        index_end = len(text)
        
    line_count = pos_end.line - pos_start.line + 1
    for i in range(line_count):
        line = text[index_start:index_end]
        col_start = pos_start.col if i == 0 else 0
        col_end = pos_end.col if i == line_count - 1 else len(line) - 1
        
        result += line + "\n"
        result += " " * col_start + "^" * (col_end - col_start)
        
        index_start = index_end
        index_end = text.find("\n", index_start + 1)
        if index_end < 0:
            index_end = len(text)
            
    return result.replace("\t", '')