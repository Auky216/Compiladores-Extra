from prettytable import PrettyTable

tokens = []  # lista de Tokens
values = []  # Lista de sus Valores
stackBase = []  # Pila para el análisis sintáctico
actions = []  # Lista para las acciones realizadas en cada paso
pila_estado_historico = []  # Historial de estados de la pila
entrada_historico = []  # Historial de la entrada en cada paso
current_token_index = 0  # Índice actual de tokens
input_expression = ""  # Almacena la entrada original
error_detected = False  # Bandera para detectar errores

# Función para obtener el token actual
def current_token():
    global current_token_index
    if current_token_index < len(tokens):
        return tokens[current_token_index]
    return None

# Función para avanzar al siguiente Token
def next_Token():
    global current_token_index
    if current_token_index < len(tokens) - 1:  # Evitar avanzar más allá del símbolo final $
        current_token_index += 1

# Función para reconocer todos los Tokens del Input
def getTokens(input):
    global tokens, values, input_expression
    input_expression = input + " $"  # Guardar la entrada original con "$"
    cont = 0
    tokens = []
    values = []
    input = input.replace(" ", "")  # Elimina los espacios

    while cont < len(input):

        # Verificar si es un número
        if input[cont].isdigit():
            num = ""  # Almacena el numero

            while cont < len(input) and input[cont].isdigit():
                num += input[cont]
                cont += 1
            tokens.append("NUMERO")  # Agrega el Token
            values.append(num)  # Agrega el valor

        # Verifica si es una letra
        elif input[cont].isalpha():
            id = ""  # Almacena el identificador

            if input[cont:cont + 5] == "print":  # Detectar la palabra clave "print"
                tokens.append("PRINT")
                values.append("print")
                cont += 5
            else:
                while cont < len(input) and input[cont].isalpha():
                    id += input[cont]
                    cont += 1
                tokens.append("ID")
                values.append(id)

        # Verifica los demás tokens
        elif input[cont] == "=":
            tokens.append("IGUAL")
            values.append("=")
            cont += 1

        elif input[cont] == "+":
            tokens.append("SUMA")
            values.append("+")
            cont += 1

        elif input[cont] == ";":
            tokens.append("PUNTO_COMA")
            values.append(";")
            cont += 1

        elif input[cont] == "(":
            tokens.append("PARENTESIS_ABIERTO")
            values.append("(")
            cont += 1

        elif input[cont] == ")":
            tokens.append("PARENTESIS_CERRADO")
            values.append(")")
            cont += 1

        else:
            print(f"Error: símbolo no reconocido {input[cont]}")
            cont += 1

    # Añadir el símbolo de fin de entrada
    tokens.append("$")
    values.append("$")

# Función para guardar el estado de la pila y la entrada en cada momento
def guardar_estado_pila_y_entrada():
    pila_estado_historico.append(list(stackBase))  # Guardar copia del estado actual de la pila
    entrada_actual = ' '.join(values[current_token_index:])  # La parte no procesada de la entrada
    entrada_historico.append(entrada_actual)

# Función Factor para analizar factores como id, números o expresiones entre paréntesis
def Factor():
    global error_detected
    token = current_token()

    # Push a la pila indicando el análisis de un Factor
    stackBase.append(f"Factor({token})")
    guardar_estado_pila_y_entrada()  # Guardar estado de la pila y entrada

    if token == "ID":  # Factor -> id
        action = f"Coincidencia ID {values[current_token_index]}"
        actions.append(action)  # Registrar la acción
        print(f"Factor: ID {values[current_token_index]}")
        next_Token()
        stackBase.pop()  # Quitar el Factor actual de la pila
        guardar_estado_pila_y_entrada()  # Guardar estado de la pila y entrada
        return True

    elif token == "NUMERO":  # Factor -> Número
        action = f"Coincidencia NUMERO {values[current_token_index]}"
        actions.append(action)  # Registrar la acción
        print(f"Factor: NUMERO {values[current_token_index]}")
        next_Token()
        stackBase.pop()  # Quitar el Factor actual de la pila
        guardar_estado_pila_y_entrada()  # Guardar estado de la pila y entrada
        return True

    else:
        error_detected = True  # Detectar error
        print(f"Error: Unexpected token {token}")
        return False

# Función Term para manejar términos
def Term():
    # Push a la pila indicando el análisis de un Term
    stackBase.append("Term()")
    guardar_estado_pila_y_entrada()  # Guardar estado de la pila y entrada
    
    if not Factor():
        return False

    stackBase.pop()  # Quitar Term actual de la pila
    guardar_estado_pila_y_entrada()  # Guardar estado de la pila y entrada
    return True

# Función Exp para manejar expresiones
def Exp():
    # Push a la pila indicando el análisis de una Exp
    stackBase.append("Exp()")
    guardar_estado_pila_y_entrada()  # Guardar estado de la pila y entrada

    if not Term():
        return False

    while current_token() == "SUMA":
        action = f"Coincidencia SUMA {values[current_token_index]}"
        actions.append(action)
        next_Token()

        if not Term():
            return False

    stackBase.pop()  # Quitar Exp actual de la pila
    guardar_estado_pila_y_entrada()  # Guardar estado de la pila y entrada
    return True

# Función Stmt para manejar declaraciones
def Stmt():
    global error_detected
    token = current_token()

    # Push a la pila indicando el análisis de un Stmt
    stackBase.append(f"Stmt({token})")
    guardar_estado_pila_y_entrada()  # Guardar estado de la pila y entrada

    if token == "ID":  # Stmt -> id = Exp
        print(f"Stmt: ID {values[current_token_index]}")
        next_Token()

        if current_token() == "IGUAL":
            print(f"Stmt: IGUAL {values[current_token_index]}")
            actions.append(f"Coincidencia IGUAL {values[current_token_index]}")
            next_Token()

            if not Exp():
                print("Error: Expected an expression after '='")
                error_detected = True
                return False

            stackBase.pop()  # Quitar Stmt actual de la pila
            guardar_estado_pila_y_entrada()  # Guardar estado de la pila y entrada
            return True
        else:
            print("Error: Expected '='")
            error_detected = True
            return False

    elif token == "PRINT":  # Stmt -> print ( Exp )
        print(f"Stmt: PRINT {values[current_token_index]}")
        next_Token()

        if current_token() == "PARENTESIS_ABIERTO":
            print(f"Stmt: PARENTESIS_ABIERTO {values[current_token_index]}")
            actions.append(f"Coincidencia PARENTESIS_ABIERTO {values[current_token_index]}")
            next_Token()

            if not Exp():
                print("Error: Expected an expression inside print()")
                error_detected = True
                return False

            if current_token() == "PARENTESIS_CERRADO":
                print(f"Stmt: PARENTESIS_CERRADO {values[current_token_index]}")
                actions.append(f"Coincidencia PARENTESIS_CERRADO {values[current_token_index]}")
                next_Token()
                stackBase.pop()  # Quitar Stmt actual de la pila
                guardar_estado_pila_y_entrada()  # Guardar estado de la pila y entrada
                return True
            else:
                print("Error: Expected ')' after expression in print()")
                error_detected = True
                return False
        else:
            print("Error: Expected '(' after 'print'")
            error_detected = True
            return False

    else:
        print(f"Error: Unexpected token {token}")
        error_detected = True
        return False

# Función StmtList para manejar listas de declaraciones
def StmtList():
    # Push a la pila indicando el análisis de un StmtList
    stackBase.append("StmtList()")
    guardar_estado_pila_y_entrada()  # Guardar estado de la pila y entrada

    if not Stmt():
        return False

    while current_token() == "PUNTO_COMA":  # Permitir múltiples declaraciones separadas por ";"
        print(f"Coincidencia PUNTO_COMA {values[current_token_index]}")
        actions.append(f"Coincidencia PUNTO_COMA {values[current_token_index]}")
        next_Token()

        if not Stmt():
            return False

    stackBase.pop()  # Quitar StmtList actual de la pila
    guardar_estado_pila_y_entrada()  # Guardar estado de la pila y entrada
    return True

# Función Program para manejar el programa completo
def Program():
    # Push a la pila indicando el análisis de un Program
    stackBase.append("Program()")
    guardar_estado_pila_y_entrada()  # Guardar estado de la pila y entrada

    if StmtList():  # El programa es una lista de declaraciones
        print("Program -> StmtList")
        stackBase.pop()  # Quitar Program actual de la pila
        guardar_estado_pila_y_entrada()  # Guardar estado de la pila y entrada
        return True
    else:
        print("Error en el análisis sintáctico del programa.")
        return False

# Función Parser que coordina todo
def Parser():
    global current_token_index, error_detected
    current_token_index = 0  # Reiniciar el índice de tokens
    error_detected = False  # Resetear el error detectado

    if Program() and not error_detected and current_token() == "$":  # Requiere que no haya errores y la entrada termine correctamente
        print("Parsing completado con éxito!")
        actions.append("Acepta")  # Añadir acción final "Acepta"
        entrada_historico.append("$")  # Finalizar con el símbolo $
    else:
        print("Error en el análisis sintáctico.")
        actions.append("Rechazo")  # Añadir acción final "Rechazo"
        entrada_historico.append("$")  # Finalizar con el símbolo $

# Probar el lexer y parser con una entrada "x = 4 +"
getTokens("x = 4; y = 5 print(x+1)")

Parser()

# Mostrar la tabla LL(1) con las acciones registradas en la pila
table = PrettyTable(["Pila", "Entrada", "Acción"])

# Agregar las acciones realizadas al analizar la entrada
for i in range(len(actions)):
    pila_estado = " ".join(pila_estado_historico[i])  # Mostrar el estado de la pila en el momento exacto
    action = actions[i]  # Acción actual
    entrada = entrada_historico[i]  # Entrada restante en este paso
    table.add_row([pila_estado, entrada, action])

print("\nTabla de acciones:")
print(table)
