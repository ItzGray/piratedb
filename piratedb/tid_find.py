def find_tid_path(manifest: dict, tid: int) -> str:
    filename = None
    for entry in manifest["m_serializedTemplates"]:
        if entry == None:
            continue
        if entry["m_id"] == tid:
            filename = entry["m_filename"].decode()
            break
    return filename

def find_school_tid(manifest: dict, tid: int) -> str:
    filename = None
    school = None
    for entry in manifest["m_serializedTemplates"]:
        if entry == None:
            continue
        if entry["m_id"] == tid:
            filename = entry["m_filename"].decode()
            break
    filenameEnding = filename[-7:]
    if filenameEnding == "WIZ.xml" or filenameEnding == "age.xml":
        school = "Witchdoctor"
    elif filenameEnding == "THF.xml" or filenameEnding == "ief.xml":
        school = "Swashbuckler"
    elif filenameEnding == "RNG.xml" or filenameEnding == "ger.xml":
        school = "Musketeer"
    elif filenameEnding == "FTR.xml" or filenameEnding == "ter.xml":
        school = "Buccaneer"
    elif filenameEnding == "CLR.xml" or filenameEnding == "ric.xml":
        school = "Privateer"
    elif filenameEnding == "PET.xml":
        school = "Pet"
    return school