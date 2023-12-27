import streamlit as st 
import pandas as pd
from kodo_function import reconcile
import os
import streamlit_authenticator as stauth
import pickle 
from pathlib import Path 
import yaml
from PIL import Image
import time
import plotly.graph_objects as go
import base64
from page_config import page_setup
from login_page import login_status


st.set_page_config(layout="wide",initial_sidebar_state ="collapsed")
page_setup()
state = st.session_state

authentication_status = login_status()


if authentication_status == False:
    space, login, space = st.columns([1,3,1])
    with login:
        st.error("Username/Password is incorrect")

if authentication_status:
    #authenticator.logout('Logout', 'sidebar')
    time.sleep(0.1)
    def landing_page():
        st.markdown('''
        <style>
        .css-9s5bis.edgvbvh3 {
        display: block;
        }
        </style>
        ''', unsafe_allow_html=True)
        #with title:
        # emp,title,emp = st.columns([2,2,2])
        # with title:
        
        if 'submit_ra' not in state:
            state.submit_ra= False
        if 'response_ra' not in state:
            state.response_ra = []
        st.markdown("<h2 style='text-align: center; padding:0'>Bank Reconciliation</h2>", unsafe_allow_html=True)
        #st.write('###')
        custom_combined_report, trf_to_bank, submit = file_upload_form()
        #print(warehouse_reports)
        # try:
        if submit:
            state.submit_ra = True
            #print(warehouse_reports)
            #print(submit)
                #print(shipment_instructions_df)
            #with st.spinner('Please wait'):
            try:
                delete_temp()
            except:
                print()

            reconcile(custom_combined_report, trf_to_bank)
            #state.response = [payment_report_df, returns_report_df, reimbursement_report, inventory_ledger_df]
            emp, but, empty = st.columns([2.05,1.2,1.5])
            with but:
                st.write("###")
                with open('kodo_reconciliation.xlsx', 'rb') as my_file:
                    click = st.download_button(label = 'Download in Excel', data = my_file, file_name = 'kodo_reconciliation.xlsx', 
                    mime = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                    #print(click) 
            #st.write(workbook) 

        else:
            pass
            # if state.submit_ra == True:
            #     emp, but, empty = st.columns([2.05,1.2,1.5]) 
            #     with but:
            #         st.write("###")
            #         with open('kodo_reconciliation.xlsx', 'rb') as my_file:
            #             click = st.download_button(label = 'Download in Excel', data = my_file, file_name = 'kodo_reconciliation.xlsx', 
            #             mime = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        # except:
        #    st.error("Run failed, kindly check if the inputs are valid")

    def delete_temp():
        os.remove('kodo_reconciliation.xlsx')

    def zip_files():
        zipObj = ZipFile("sample.zip", "w")
        zipObj.write("checkpoint")
        zipObj.write("model_hyperparameters.json")
        # close the Zip File
        zipObj.close()

    def file_upload_form():
        colour = "#89CFF0"
        with st.form(key = 'ticker',clear_on_submit=False):
            text, upload = st.columns([2.5,3]) 
            with text:
                st.write("###")
                st.write("###")
                st.write(f'<h5>{"&nbsp; Upload Custom Combined Report:"}</h5>', unsafe_allow_html=True)
            with upload:
                custom_combined_report = st.file_uploader("",key = 'ccr')

            text, upload = st.columns([2.5,3])
            with text:
                st.write("###")
                st.write("###")
                st.write(f'<h5>{"&nbsp; Upload Transfer to Bank:"}<h5>', unsafe_allow_html=True)
            with upload:
                trf_to_bank = st.file_uploader("",key = 'ttb')

            # text, upload = st.columns([2.5,3])
            # with text:
            #     st.write("###")
            #     st.write("###")
            #     st.write(f'<h5>{"&nbsp; Upload Scheme Details:"}<h5>', unsafe_allow_html=True)
            # with upload:
            #     scheme_details = st.file_uploader("",key = 'schemes')
            
            a,button,b = st.columns([2,1.2,1.5]) 
            with button:
                st.write('###')
                submit = st.form_submit_button(label = "Start Reconciliation")
                #submit = st.button(label="Start Reconciliation")

        return custom_combined_report, trf_to_bank, submit
        

        

    landing_page()

