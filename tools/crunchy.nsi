#MOVE IT TO UP-LEVEL DIRECTORY BEFORE USING IT.

# include the modern UI
!include "MUI.nsh"

# set the version and some basic options
!define VERSION "VERSION"
Name "Crunchy ${VERSION}"
OutFile "crunchy-${VERSION}-win.exe"
InstallDir "$PROGRAMFILES\Crunchy"

# warn on abort
!define MUI_ABORTWARNING

#----------------------------------------------------

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "crunchy\LICENSE.txt"
!insertmacro MUI_PAGE_COMPONENTS
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

UninstPage uninstConfirm
UninstPage instfiles

!insertmacro MUI_LANGUAGE "English"
#----------------------------------------------------
Section "Crunchy" SecMain

    SetOutPath "$INSTDIR"
    File /r /x .svn /x *.pyc /x *.pyo crunchy\*
    WriteUninstaller "uninstall.exe"

SectionEnd


#----------------------------------------------------
Section "Start Menus and Desktop Shortcut" SecShortcut

    CreateDirectory "$SMPROGRAMS\Crunchy"
    CreateShortCut "$SMPROGRAMS\Crunchy\Start Crunchy.lnk" "$INSTDIR\crunchy.py"
    CreateShortCut "$SMPROGRAMS\Crunchy\Uninstall Crunchy.lnk" "$INSTDIR\uninstall.exe"
    CreateShortCut "$DESKTOP\Start Crunchy.lnk" "$INSTDIR\crunchy.py"

SectionEnd

#----------------------------------------------------
Section "Uninstall"
  Delete $INSTDIR\uninstall.exe
  RMDir /r $INSTDIR
  RMDir /r $SMPROGRAMS\Crunch
  Delete "$DESKTOP\Start Crunchy.lnk"
SectionEnd

# we need an installer - this should probably be based on
# http://nsis.sourceforge.net/Uninstall_only_installed_files
