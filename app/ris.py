# parse RIS format to DF
# @Date: May 13th,2022
# @Author: Shouqiang Ye
# Function: convert RIS file to CVS, and download

from config import Config
import io, os, sys
from urllib.request import urlopen
import pandas as pd
from copy import deepcopy
import rispy
from pprint import pprint


def get_property(entry, field_str):
    try:
        return entry[field_str]
    except:
        return ""


def ris2csv(file):
    # mapping = TAG_KEY_MAPPING  # default mapping
    mapping = deepcopy(rispy.TAG_KEY_MAPPING)  # default mapping
    mapping["AU"] = "AU"  # adjust default mapping
    # set a temp ris file in upload directory <-- binary file to string
    # temp_ris_full_filepath = current path + '/uploads/temp.ris'
    # define filename constant
    # f.save(os.path.join(Config.UPLOAD_FOLDER, filename))
    # my_file = open(os.path.join(Config.UPLOAD_FOLDER, "UNC_COVID19_Research_May-2021.ris"), 'r')
    # entries = rispy.load(my_file, mapping=mapping)

    """
    with open(os.path.join(Config.UPLOAD_FOLDER, file), 'r') as bibliography_file:
        entries = rispy.load(bibliography_file, mapping=mapping)
    """
    with open(os.path.join(Config.UPLOAD_FOLDER, file), 'r') as bibliography_file:
        entries = rispy.load(bibliography_file, mapping=mapping, encoding='utf-8-sig')
    # read in RIS . output is a python dict.

    # initialize lists to hold properties
    TY = []  # type_of_reference
    AB = []  # abstract
    AN = []  # accession number
    AU = []  # authors
    RN = []  # research notes
    C1 = []  # custom1
    C2 = []  # custom2
    #    C3=[] # custom3
    #    C4=[] # custom4
    #    C5=[] # custom5
    DB = []  # name_of_database
    DO = []  # doi
    LB = []  # label
    M1 = []  # note
    M3 = []  # type_of_work
    N1 = []  # notes
    PY = []  # year
    SP = []  # start_page
    ST = []  # short_title
    T2 = []  # secondary_title
    TI = []  # title
    UR = []  # url
    VL = []  # volume
    ID = []  # id

    for entry in entries:  # loop over records, get properties, and append to property lists
        id_t = get_property(entry, 'id')
        title_t = get_property(entry, 'title')
        journal_t = get_property(entry, 'secondary_title')
        full_author_list_t = get_property(entry, 'AU')
        full_author_t = "; ".join(full_author_list_t)
        year_t = get_property(entry, 'year')
        ty_t = get_property(entry, 'type_of_reference')
        ab_t = get_property(entry, 'abstract')
        an_t = get_property(entry, 'accession_number')
        rn_t = get_property(entry, 'research_notes')
        c1_t = get_property(entry, 'custom1')
        c2_t = get_property(entry, 'custom2')
        #        c3_t=get_property(entry, 'custom3')
        #        c4_t=get_property(entry, 'custom4')
        #        c5_t=get_property(entry, 'custom5')
        db_t = get_property(entry, 'name_of_database')
        do_t = get_property(entry, 'doi')
        lb_t = get_property(entry, 'label')
        m1_t = get_property(entry, 'note')
        m3_t = get_property(entry, 'type_of_work')
        n1_t = get_property(entry, 'notes')
        sp_t = get_property(entry, 'start_page')
        st_t = get_property(entry, 'short_title')
        ur_t = get_property(entry, 'url')
        vl_t = get_property(entry, 'volume')
        id_t = get_property(entry, 'id')
        ID.append(id_t)
        TI.append(title_t)
        T2.append(journal_t)
        AU.append(full_author_t)
        PY.append(year_t)
        TY.append(ty_t)
        AB.append(ab_t)
        AN.append(an_t)
        RN.append(rn_t)
        C1.append(c1_t)
        C2.append(c2_t)
        #        C3.append(c3_t)
        #        C4.append(c4_t)
        #        C5.append(c5_t)
        DB.append(db_t)
        DO.append(do_t)
        LB.append(lb_t)
        M1.append(m1_t)
        M3.append(m3_t)
        N1.append(n1_t)
        SP.append(sp_t)
        ST.append(st_t)
        UR.append(ur_t)
        VL.append(vl_t)
    
    df = pd.DataFrame({'ID': ID,
                       'TI': TI,
                       'T2': T2,
                       'AU': AU,
                       'AN': AN,
                       'PY': PY,
                       'TY': TY,
                       'AB': AB,
                       'RN': RN,
                       'C1': C1,
                       'C2': C2,
                       #                          'C3': C3,
                       #                          'C4': C4,
                       #                          'C5': C5,
                       'DB': DB,
                       'DO': DO,
                       'M1': M1,
                       'M3': M3,
                       'N1': N1,
                       'SP': SP,
                       'ST': ST,
                       'UR': UR,
                       'VL': VL,
                       'LB': LB,
                       })

    df["TAB"] = df["TI"].map(str) + ' ' + df["AB"].map(str)  # create TAB field for Text analysis

    return df



def isNaN(num):  # check if not a number or blank string
    flag = False
    if num != num:  # check for NaN
        flag = True
    if num == "":  # check for blank
        flag = True
    return flag

# return ris file
# parameter: df: input dataframe, file: output filename including filepath
def csv2ris(df, file):
    try:
        # open write file with file name
        out_file = open(file, 'w')
        # col_order=["TY","AB","AN","AU","C1","C2","C3","C4","C5","DB","DO","ID","LB","M1","M3",
        # "N1","PY","RN","SP","ST","T2","TI","UR","VL"]
        col_order = ["TY",
                     "AB",
                     "AN",
                     "AU",
                     "RN",
                     "C1",
                     "C2",
                     "C3",
                     "C4",
                     "C5",
                     "DB",
                     "DO",
                     "ID",
                     "LB",
                     "M1",
                     "M3",
                     "N1",
                     "PY",
                     "RN",
                     "SP",
                     "ST",
                     "T2",
                     "TI",
                     "UR",
                     "VL"]
        # loop over rows
        for index, row in df.iterrows():
            # loop over columns
            for col in col_order:
                if col in list(df):
                    if not isNaN(row[col]):  # if no blank nothing
                        if col == "AU":  # for author field, output multiple authors on distinct lines
                            alist = row[col].split(";")
                            for x in alist:
                                # strip blank space before x; note print statement adds a space between items
                                out_file.write(col + "  - " + str.strip(x))
                                out_file.write("\n")
                        else:
                            # change int type to str for some fields, like AN, PY
                            out_file.write(col + "  - " + str(row[col]))
                            out_file.write("\n")
                    else:
                        out_file.write(col + "  - ")
                        out_file.write("\n")
            out_file.write("ER  - \n")
            out_file.write("\n")
            out_file.write("\n")
        out_file.close()
    except FileNotFoundError as err:
        print('Error: cannot find file,', file)
        print('Error:', err)
    except OSError as err:
        print('Error: cannot access file,', file)
        print('Error:', err)
    except ValueError as err:
        print('Error: invalid data found in file', file)
        print('Error:', err)
    except Exception as err: # catch all error handler, if the above handlers do not apply
        print('An unknown error occurred')
        print('Error:', err)