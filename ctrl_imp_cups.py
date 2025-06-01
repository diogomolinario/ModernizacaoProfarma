#!/usr/bin/python3

import subprocess
import sys
import time
import os
import re
import tempfile
import curses

COR_CABECALHO = 1
COR_ITENS = 2
COR_FONTE = 3
COR_BARRA = 4

# Comandos auxiliares
def run_cmd(args):
    return subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

def read_status_lines(printer):
    return run_cmd(['lpstat', '-p', printer]).stdout, run_cmd(['lpstat', '-a', printer]).stdout

def verificar_status(status_line, accepting_line):
    if "disabled" in status_line.lower():
        return "ERRO", "PAUSADA;"
    elif "not accepting" in accepting_line.lower():
        return "ERRO", "REJEITANDO TRABALHOS;"
    elif "filter failed" in status_line.lower():
        return "ERRO", "FILTRO COM FALHA;"
    return "OK", ""

def qtd_trabalhos(printer):
    total = run_cmd(['lpstat', '-o', printer]).stdout.count('\n')
    erros = run_cmd(['lpstat', '-W', 'not-completed', '-o', printer])
    total += len([l for l in erros.stdout.splitlines() if re.search(r'(stopped|aborted|canceled)', l, re.IGNORECASE)])
    return total

def reinicia_impressora(outfile, impressora):
    with open(outfile, 'w') as f:
        try:
            subprocess.run(['cancel', '-a', impressora], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(['cupsenable', impressora], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(['cupsaccept', impressora], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            f.write("0;OK\n")
        except Exception as e:
            f.write(f"1;FALHA AO REINICIAR;{str(e).upper()}\n")

def verifica_e_reinicia(printer):
    if qtd_trabalhos(printer) == 0:
        with tempfile.NamedTemporaryFile(delete=False, mode='w+', prefix='valida_', suffix='.txt', dir='/tmp') as tmp:
            temp_path = tmp.name
        reinicia_impressora(temp_path, printer)
        with open(temp_path, 'r') as tf:
            if tf.readline().strip().startswith("0;OK"):
                os.remove(temp_path)
                return read_status_lines(printer)
        os.remove(temp_path)
    return read_status_lines(printer)

def consulta_impressoras(log_path):
    try:
        with open(log_path, 'w') as f:
            result = run_cmd(['lpstat', '-p'])
            printers = re.findall(r'^printer (\S+)', result.stdout, re.MULTILINE)
            for p in printers:
                s_line, a_line = verifica_e_reinicia(p)
                status, motivo = verificar_status(s_line, a_line)
                f.write(f"{p};{status};{motivo}\n")
    except:
        with open(log_path, 'w') as f:
            f.write("FALHA AO CONSULTAR IMPRESSORAS\n")

def consulta_impressora_interativa(log_temp):
    consulta_impressoras(log_temp)
    if not os.path.exists(log_temp):
        return ""
    with open(log_temp, 'r') as f:
        linhas = [l.strip().split(';')[0] for l in f.readlines() if ';OK;' in l]
    if not linhas:
        return ""

    def mostrar(stdscr):
        curses.curs_set(0)
        sel, top = 0, 0

        altura_total = 15
        largura_total = 27  # 25 úteis + bordas

        win = curses.newwin(altura_total, largura_total, 0, 0)
        win.keypad(True)

        while True:
            win.erase()

            # Linha 1 - topo
            win.addstr(1, 0, '+' + '-' * 25 + '+')

            # Linha 2 - cabeçalho com reverse apenas no conteúdo
            win.addstr(2, 0, '|')
            win.attron(curses.A_REVERSE)
            win.addstr(2, 1, 'IMPRESSORAS'.center(25))
            win.attroff(curses.A_REVERSE)
            win.addstr(2, 26, '|')

            # Linha 3 - separador
            win.addstr(3, 0, '+' + '-' * 25 + '+')

            # Linhas 4–10: impressoras
            for i in range(7):
                idx = top + i
                nome = linhas[idx][:24].ljust(24) if idx < len(linhas) else " " * 24
                barra = '#' if idx == sel else ' '

                win.addstr(4 + i, 0, '|')
                if idx == sel:
                    win.attron(curses.A_REVERSE)
                    win.addstr(4 + i, 1, nome + barra)
                    win.attroff(curses.A_REVERSE)
                else:
                    win.addstr(4 + i, 1, nome + barra)
                win.addstr(4 + i, 26, '|')

            # Linha 11 - separador
            win.addstr(11, 0, '+' + '-' * 25 + '+')

            # Linha 12 - mensagem com reverse apenas no conteúdo
            win.addstr(12, 0, '|')
            win.attron(curses.A_REVERSE)
            win.addstr(12, 1, 'Msg: Up/Dn - ESC - Enter'.ljust(25))
            win.attroff(curses.A_REVERSE)
            win.addstr(12, 26, '|')

            # Linha 13 - rodapé
            win.addstr(13, 0, '+' + '-' * 25 + '+')

            win.refresh()
            key = win.getch()
            if key in [27, 10, 13]:  # ESC ou ENTER
                return linhas[sel] if key != 27 else ""
            elif key == curses.KEY_UP and sel > 0:
                sel -= 1
                if sel < top:
                    top -= 1
            elif key == curses.KEY_DOWN and sel < len(linhas) - 1:
                sel += 1
                if sel > top + 6:
                    top += 1

    try:
        return curses.wrapper(mostrar)
    finally:
        if os.path.exists(log_temp):
            os.remove(log_temp)

def consulta_impressora_unica(log_path, printer):
    if not printer:
        with open(log_path, 'w') as f:
            f.write("1;IMPRESSORA NAO INFORMADA\n")
        return 2
    try:
        result = run_cmd(['lpstat', '-p', printer])
        if "Unknown" in result.stderr:
            raise Exception("IMPRESSORA NAO EXISTE")
        s_line, a_line = verifica_e_reinicia(printer)
        status, motivo = verificar_status(s_line, a_line)
        with open(log_path, 'w') as f:
            f.write(f"{printer};{status};{motivo}\n")
    except:
        with open(log_path, 'w') as f:
            f.write("1;IMPRESSORA NAO EXISTE\n")
        return 2

def impressao(log_path, impressora, arq_impressao):
    if not log_path:
        return 1

    if not impressora:
        with open(log_path, 'w') as f:
            f.write("1;PARAMETROS IMPRESSORA NAO INFORMADO\n")
        return 2

    if not arq_impressao:
        with open(log_path, 'w') as f:
            f.write("1;PARAMETROS ARQ. P/ IMPRESSAO NAO INFORMADO\n")
        return 2
    if not os.path.isfile(arq_impressao):
        with open(log_path, 'w') as f:
            f.write("1;ARQUIVO DE IMPRESSAO NAO EXISTE\n")
        return 2

    if not os.access(arq_impressao, os.R_OK):
        with open(log_path, 'w') as f:
            f.write("1;ARQUIVO SEM PERMISSAO DE LEITURA\n")
        return 2

    temp_status = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, mode='w+', prefix='valida_', suffix='.txt', dir='/tmp') as temp_file:
            temp_status = temp_file.name

        consulta_impressora_unica(temp_status, impressora)

        with open(temp_status, 'r') as f:
            linha = f.readline().strip()
            partes = linha.split(';')
            if len(partes) >= 2 and partes[1] == "ERRO":
                with open(log_path, 'w') as log:
                    log.write(f"ERRO;{impressora} NAO PODE IMPRIMIR, {partes[2].upper()}.\n")
                return 2
    finally:
        if temp_status and os.path.exists(temp_status):
            os.remove(temp_status)

    cmd = f"lp -d {impressora} {arq_impressao}"

    try:
        result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        if result.returncode != 0:
            raise Exception("FALHA AO ENVIAR PARA IMPRESSAO")

        match = re.search(r'request id is (\S+)', result.stdout)
        job_id = match.group(1).split('(')[0].strip() if match else ""

        for _ in range(6):  # tenta por até ~18 segundos
            time.sleep(3)
            try:
                details = subprocess.check_output(['lpstat', '-l', '-o'], stderr=subprocess.DEVNULL, universal_newlines=True)
                found = False
                bloco = []

                for line in details.splitlines():
                    if job_id in line:
                        found = True
                        bloco = [line]
                    elif found:
                        if line.strip() == "":
                            break
                        bloco.append(line)

                if found:
                    upper_block = " ".join(" ".join(bloco).upper().split())
                    if "FILTER FAILED" in upper_block or "JOB-COMPLETED-WITH-ERRORS" in upper_block:
                        with open(log_path, 'w') as f:
                            f.write(f"ERRO;{upper_block}\n")
                        subprocess.run(['cancel', job_id], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        return
                    elif "COMPLETED" in upper_block or "PRINTED" in upper_block:
                        with open(log_path, 'w') as f:
                            f.write("IMPRESSO;FINALIZADO COM SUCESSO\n")
                        return
                else:
                    # Job desapareceu da fila = considerado impresso
                    with open(log_path, 'w') as f:
                        f.write("IMPRESSO;FINALIZADO COM SUCESSO\n")
                    return
            except:
                pass

        with open(log_path, 'w') as f:
            f.write(f"ERRO;{cmd} - DESCONHECIDO, TEMPO LIMITE EXCEDIDO PARA VALIDACAO\n")
        subprocess.run(['cancel', job_id], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return 2

    except Exception as e:
        with open(log_path, 'w') as f:
            msg = f"ERRO;{cmd} - FALHA: {str(e).upper()}"
            msg = " ".join(msg.split())
            f.write(f"{msg}\n")            
        return 2

# MAIN
def main():
    if len(sys.argv) < 3:
        return 1

    func = sys.argv[1].lower()
    log_path = sys.argv[2]
    if not os.access(log_path, os.W_OK):
        #with open(log_path, 'w') as f:
        #    f.write("1;ARQUIVO SEM PERMISSAO DE LEITURA\n")
        return 1
    

    if func == "consulta-impressoras":
        consulta_impressoras(log_path)
        return 0
    elif func == "consulta-impressora-unica":
        return consulta_impressora_unica(log_path, sys.argv[3] if len(sys.argv) >= 4 else None)
    elif func == "impressao":
        impressora = sys.argv[3] if len(sys.argv) >= 4 else None
        if not impressora:
            with tempfile.NamedTemporaryFile(delete=False, mode='w+', suffix='.txt', dir='/tmp') as tmp:
                tmp_path = tmp.name
            impressora = consulta_impressora_interativa(tmp_path)
            if not impressora:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
                return 0
        return impressao(log_path, impressora, sys.argv[4] if len(sys.argv) >= 5 else None)
    else:
        with open(log_path, 'w') as f:
            f.write("FUNCAO DESCONHECIDA\n")
        return 2

if __name__ == "__main__":
    exit(main())