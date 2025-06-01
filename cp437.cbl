       IDENTIFICATION  DIVISION.
       PROGRAM-ID.     cp437.
       AUTHOR.         DIOGO.
      *---------------------------------------------------------------*
       ENVIRONMENT     DIVISION.
       CONFIGURATION   SECTION.
       SPECIAL-NAMES.
                       DECIMAL-POINT IS COMMA.
       INPUT-OUTPUT    SECTION.
       FILE-CONTROL.
       DATA           DIVISION.
       FILE           SECTION.
       WORKING-STORAGE SECTION.
       01 conf                         pic x(001)          value space.
       SCREEN SECTION.
       01 tela.
          02 blank SCREEN.
          02 line 02 COLUMN 01 "".
          02 line 03 COLUMN 01 "".
          02 line 03 COLUMN 02 "     IMPRESSORAS       "
              HIGHLIGHT REVERSE-VIDEO.
          02 line 03 COLUMN 25 "".
          02 line 04 COLUMN 01 "".
          02 line 05 COLUMN 01 " IMPRESSORA01          ".
          02 line 06 COLUMN 01 "".
          02 line 06 COLUMN 02 " IMPRESSORA02         #"
              HIGHLIGHT REVERSE-VIDEO.
          02 line 06 COLUMN 25 "".
          02 line 07 COLUMN 01 " IMPRESSORA03          ".
          02 line 08 COLUMN 01 " IMPRESSORA04          ".
          02 line 09 COLUMN 01 " IMPRESSORA05          ".
          02 line 10 COLUMN 01 " IMPRESSORA06          ".
          02 line 11 COLUMN 01 " IMPRESSORA07          ".
          02 line 12 COLUMN 01 "".
          02 line 13 COLUMN 01 "".
          02 line 13 COLUMN 02 "  Use: "
              HIGHLIGHT REVERSE-VIDEO.
          02 line 13 COLUMN 09  from "Up"
              HIGHLIGHT REVERSE-VIDEO.
          02 line 13 COLUMN 11 " "
                                REVERSE-VIDEO.
          02 line 13 COLUMN 12 from "Dw"
              HIGHLIGHT REVERSE-VIDEO.
          02 line 13 COLUMN 14 " Esc Enter."
              HIGHLIGHT REVERSE-VIDEO.
          02 line 13 COLUMN 25 "".
          02 line 14 COLUMN 01 "".
          02 LINE 03 COLUMN 26 from X"DBDB".
          02 LINE 04 COLUMN 26 from X"DBDB".
          02 LINE 05 COLUMN 26 from X"DBDB".
          02 LINE 06 COLUMN 26 from X"DBDB".
          02 LINE 07 COLUMN 26 from X"DBDB".
          02 LINE 08 COLUMN 26 from X"DBDB".
          02 LINE 09 COLUMN 26 from X"DBDB".
          02 LINE 10 COLUMN 26 from X"DBDB".
          02 LINE 11 COLUMN 26 from X"DBDB".
          02 LINE 12 COLUMN 26 from X"DBDB".
          02 LINE 13 COLUMN 26 from X"DBDB".
          02 LINE 14 COLUMN 26 from X"DBDB".
          02 LINE 15 COLUMN 02 pic x(026) from all X"DB".




       procedure division.
       INICIO.
           display tela
           accept conf at 2001
           stop run.