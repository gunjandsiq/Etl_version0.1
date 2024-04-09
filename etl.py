
from flask import Blueprint
import pandas as pd
from sentry_sdk import capture_exception

etl_bp = Blueprint("df",__name__)
class DFHelper:
    def reindex(self,df,columns):
        try:
            df = df.reindex(columns=columns)
            return df
        except Exception as e: 
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)

    def rename(self,df,columns):
        try:
            df = df.rename(columns=columns, inplace=True)
            return df
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)

    def merge(self, df, df_mergewith, how, left_on, right_on):
        try:
            df = df.merge(df_mergewith, how=how, left_on=left_on, right_on=right_on)
            return df
        except Exception as e:
           print(f"An error occurred: {e}")
           capture_exception(e)
           return str(e)

    def drop(self,df,columns):
        try:
            df = df.rename(columns=columns, inplace = True)
            return df
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)
