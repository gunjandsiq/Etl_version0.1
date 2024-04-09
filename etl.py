
from flask import Blueprint
import pandas as pd
from sentry_sdk import capture_exception

etl_bp =Blueprint("df",__name__)


class DFHelper:
    def __init__(self):
        self.df = pd.read_csv('customer-100.csv')
    
    def reindex(self,df,columns):
        try:
            df = self.df.reindex(columns=columns)
            return df
        except Exception as e: 
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)

    def rename(self,df,columns):
        try:
            df = self.df.rename(columns=columns)
            return df
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)

    def merge(self, df, df_mergewith, how, on):
        try:
            df = self.df.merge(df_mergewith, how=how, on=on)
            return df
        except Exception as e:
           print(f"An error occurred: {e}")
           capture_exception(e)
           return str(e)

    def drop(self,df,columns):
        try:
            df = self.df.drop(columns=columns)
            return df
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)

    def insert(self,df,columns):
        try:
            df = self.df.insert(columns = columns)
            return df
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)