import os
import shutil
import time
import threading

from .DNASerializer import DNASerializer


class AutoSaver:
    autoSaverToggled = False
    autoSaverInterval = 15.0
    maxAutoSaveCount = 10.0

    @staticmethod
    def initializeAutoSaver():
        threading.Thread(target = AutoSaver.autoSaverProcess, daemon = True).start()
        # Creates 'autosaves' directory in user data directory
        if not os.path.isdir('leveleditor/autosaves'):
            os.mkdir('leveleditor/autosaves')
            print('Created "autosaves" dir')

    @staticmethod
    def autoSaverProcess():
        while True:
            autoSaverInterval = AutoSaver.autoSaverInterval * 60  # Converts global autoSaverInterval to minutes
            # Loops without doing anything if auto saver isn't toggled
            if AutoSaver.autoSaverToggled is False:
                time.sleep(0.1)

            while AutoSaver.autoSaverToggled is True:
                # outputFile filename is empty, which may occur if filename is left blank in file prompt
                if DNASerializer.outputFile is None:
                    print('No file loaded, exiting auto saving loop...')
                    DNASerializer.autoSaveCount = 0
                    DNASerializer.autoSaverMgrRunning = False
                    AutoSaver.autoSaverToggled = False
                    break

                # Epoch time of next auto save
                endTime = time.time() + autoSaverInterval
                # Loops until endTime is reached or the auto saver is un-toggled by user
                while time.time() <= endTime and AutoSaver.autoSaverToggled is True:
                    time.sleep(0.1)
                # Only auto save if auto save is toggled
                if AutoSaver.autoSaverToggled is True:
                    AutoSaver.manageAutoSaveFiles()
                    # Sets autoSaveCount
                    if DNASerializer.autoSaveCount >= AutoSaver.maxAutoSaveCount:
                        DNASerializer.autoSaveCount = AutoSaver.maxAutoSaveCount
                    else:
                        DNASerializer.autoSaveCount += 1

    @staticmethod
    def manageAutoSaveFiles():
        DNASerializer.autoSaverMgrRunning = True
        autoSaveCount = int(DNASerializer.autoSaveCount)

        # Defining outputFile name properties
        base = os.path.basename(DNASerializer.outputFile)
        dir = os.path.dirname(DNASerializer.outputFile)
        basename, extension = os.path.splitext(base)

        # Renames output file to auto save file naming convention
        if autoSaveCount == 0:
            # Only save & manage 'latest' file
            if AutoSaver.maxAutoSaveCount == 0:
                # Only save auto save latest file
                if basename[-16:] == '_autosave-latest':
                    DNASerializer.outputDNADefaultFile()  # Saves working DNA file
                    return
            DNASerializer.outputFile = os.path.join(dir, 'autosaves', basename + '_autosave-latest' + extension)
            # Replaces any back slashes in outputFile with forward slashes
            DNASerializer.outputFile = DNASerializer.outputFile.replace('\\', '/')
            # Creates new 'autosaves' directory if none is found
            # This also accounts for if the directory of outputFile is not in the default user data folder
            if not os.path.isdir(os.path.join(dir, 'autosaves')):
                os.mkdir(os.path.join(dir, 'autosaves'))

        # Deletes 'latest' from filename
        basename = basename[:-6]

        # Copies auto save files
        while autoSaveCount != 0:
            filename = os.path.join(dir, basename + str(autoSaveCount) + extension)
            oldFilename = os.path.join(dir, basename + str(autoSaveCount - 1) + extension)
            # Copies working auto save file
            if autoSaveCount == 1:
                shutil.copy2(DNASerializer.outputFile, filename)
            # Incrementally copies each auto save file (i.e. 3400_autosave-1.dna -> 3400_autosave-2.dna)
            if autoSaveCount > 1:
                shutil.copy2(oldFilename, filename)
            autoSaveCount -= 1

        DNASerializer.outputDNADefaultFile()  # Saves working DNA file
        DNASerializer.autoSaverMgrRunning = False
