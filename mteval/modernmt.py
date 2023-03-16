# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/10_modernmt.ipynb.

# %% auto 0
__all__ = ['modernmttranslate']

# %% ../nbs/10_modernmt.ipynb 7
import uuid
import os
from langcodes import *
from modernmt import ModernMT

class modernmttranslate:
    """
    Class to get translations from the ModernMT API
    """
    def __init__(self,adaptive=False,adaptation_tm=None,reference_tms=None):
        """Constructor of modernmttranslate class"""
        # TBD: there is probably a good way to read the version from the configuration in setup.py
        self._mmt = ModernMT(os.getenv('MMT_API_KEY'),"mteval","0.0.1")
        self._languages_cache = []
        self.adaptive = adaptive
        if adaptive:
            if adaptation_tm:
                self._adaptation_tm_id = adaptation_tm
            else:
                self._adaptation_tm_id = self.create_adaptation_tm()
                
    def create_adaptation_tm(self):
        """
        Function to create empty translation memory (TM) for adaptative MT.

        Returns
        -------
        int
            Returns ModernMT ID for created translation memory.
        """
        
        adaptation_tm = self._mmt.memories.create(str(uuid.uuid4()))
        adaptation_tm_id = adaptation_tm.id
        
        return adaptation_tm_id
    
    def add_reference_translation(self, tuid, sourcelang, targetlang, source, reference):
        # TBD: should tuid be an integer or more universally a string?
        """Function to submit a new reference translation (most often post-edited translation) to the adaptation TM.
        
        Parameters
        ----------
        tuid :
            Unique ID of the translation segment - if it exists, the segment gets overwritten
        sourcelang : str
            Source language identifier (BCP-47 format).
        targetlang : str
            Target language identifier (BCP-47 format).
        source : str
            Source text.
        reference : str
            Reference translation, possibly post-edited from machine translation.

        """
        import_job = self._mmt.memories.add(self._adaptation_tm_id, sourcelang, targetlang, source, reference, str(tuid))
        
        # Waiting for the import job is blocking - this is acceptable for evaluation, but probably not for live translation
        import_job_id = import_job.id
        finished = import_job.progress
        while not finished:
            import_job = self._mmt.memories.get_import_status(import_job_id)
            finished = import_job.progress   
        
        return
        
    def check_langpair(self, sourcelang, targetlang):
        """Function to verify if a language pair identified by language ids is supported
        
        Parameters
        ----------
        sourcelang : str
            Source language identifier (BCP-47 format).
        targetlang : str
            Target language identifier (BCP-47 format).
            
        Returns
        -------
        bool
            Returns `True` if language pair is supported, otherwise `False`.
        
        """
        supported_languages = self._languages_cache
        # Cached language array empty if not initialized yet
        if not supported_languages:
            supported_languages = self._mmt.list_supported_languages()
            self._languages_cache = supported_languages
            
        language_pair_supported = False
        if tag_is_valid(sourcelang) and tag_is_valid(targetlang):
            if sourcelang in supported_languages and targetlang in supported_languages:
                language_pair_supported = True
        
        return language_pair_supported

    def translate_text(self,sourcelang, targetlang, text):
        """Function to translate text into the target language
        
        Parameters
        ----------
        sourcelang : str
            Source language identifier (BCP-47 format).
        targetlang : str
            Target language identifier (BCP-47 format).
        text : str
            Source text that is to be translated.
            
        Returns
        -------
        str
            Translated text.
        """
        translated_text = ""
        if self.check_langpair(sourcelang,targetlang):
            if self.adaptive:
                # TBD: Later need to add reference TMs too
                translation = self._mmt.translate(sourcelang, targetlang, text,hints=[self._adaptation_tm_id])
            else:
                translation = self._mmt.translate(sourcelang, targetlang, text)
            translated_text = translation.translation

        return translated_text
