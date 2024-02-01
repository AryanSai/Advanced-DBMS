import sqlparse

def select(tokens):
    print('Found SELECT!!')
    print(tokens)

def main():
    query = 'select * from friends.csv;'

    #format the query
    query = sqlparse.format(query, reindent=True, keyword_case='upper')
    
    query = query.replace('\n', ' ')

    print(query)

    tokens=query.split(' ')
    print(tokens.index('SELECT'))
    
    parsed_query = sqlparse.parse(query)[0]
    tokens = parsed_query.tokens

    for token in tokens:
        if token.value == 'SELECT':
                select(tokens)
            
main()