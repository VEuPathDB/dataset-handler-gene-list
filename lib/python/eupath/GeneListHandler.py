from subprocess import Popen

from handler_base.dataset_handler import DatasetHandler, ValidationException
import sys, re

class GeneListHandler(DatasetHandler):
    """
    This class is a specialized version of the Galaxy to EuPathDB dataset export tool.  This tool's
    specialty is furnishing user's gene list data to EuPathDB.  As with all specialty export tools, this
    tool implements 3 abstract classes.
    """

    # Name given to this type of dataset and to the expected file
    GENE_LIST_TYPE = "GeneList"
    GENE_LIST_VERSION = "1.0"
    GENE_LIST_FILE = "genelist.txt"

    def __init__(self, args):
        """
        Initializes the gene list export class with the parameters needed to accomplish the particular
        type of export.
        :param args: parameters provided from tool form
        """
        DatasetHandler.__init__(self,
                                GeneListHandler.GENE_LIST_TYPE,
                                GeneListHandler.GENE_LIST_VERSION,
                                None,  # Validation is done in-process in validate_datasets
                                args)
        # For the gene list export, project_ids parameter expected in addition to base 7.
        if len(args) < 8:
            raise ValidationException("The tool was passed an insufficient numbers of arguments.")

        # Data for the input given by the user
        self._dataset_file_path = args[7]

        # Overriding the dataset genome reference with that provided via the form.
        if len(args[6].strip()) == 0:
            raise ValidationException("ProjectIds must be specified.")
        self._projects = args[6].split(",")

    def validate_datasets(self):
        error = None
        dataset_files = self.identify_dataset_files()

        if len(dataset_files) != 1:
            error = "A gene list dataset should have only one file."
        else:
            with open(dataset_files[0]['path'], 'r') as source_file:
                for line in source_file:
                    if re.search(r"\s", line.strip()):
                        error = "No lines in a gene list file should contain embedded whitespace."
        if error is not None:
            sys.stderr.write("Error: " + error)
            sys.exit(1)

    def identify_dependencies(self):
        """
        The appropriate dependency(ies) will be determined by the reference genome selected - only one for now
        The EuPathDB reference genomes will have a project id, a EuPath release number, and a genome description
        all separated by a dash in the first instance and an underscore in the second instance.
        :return: list containing the single dependency with the component parts parsed out (only one for now)
        """
        return []

    def identify_projects(self):
        """
        The appropriate project(s) will be determined by the reference genome selected - only one for now
        The project name must be listed in the SUPPORTED_PROJECTS array.  Failure to find it will be
        regarded as a validation exception.
        :return: list containing the single relevant EuPath project (only one for now)
        """
        return self._projects

    def identify_dataset_files(self):
        """
        The user provided gene list file is combined with the name EuPathDB expects
        for such a file
        :return: A list containing the single dataset file accompanied by its EuPathDB designation.
        """
        return [{"name": self.GENE_LIST_FILE, "path": self._dataset_file_path}]