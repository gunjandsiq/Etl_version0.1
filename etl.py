
from flask import Blueprint
import pandas as pd
from sentry_sdk import capture_exception

etl_bp = ("df",__name__)
class DFHelper:

    def reindex(self,df,columns):
        try:
            df.reindex(columns=columns)
            return df
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)

    def rename(self,df,columns):
        try:
            df.rename(columns=columns)
            return df
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)

    def merge(self,df,columns):
        try:
            df.rename(columns=columns)
            return df
        except Exception as e:
           print(f"An error occurred: {e}")
           capture_exception(e)
           return str(e)

    def drop(self,df,columns):
        try:
            df.rename(columns=columns, inplace = True)
            return df
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)
