import pandas as pd
import recordlinkage
import datetime
import numpy as np
import sys

def reconcile(custom_combined_report, trf_to_bank):
	custom_combined_report = pd.read_excel(custom_combined_report)
	custom_combined_report['amount'] = custom_combined_report['amount'].round(decimals=2)
	custom_combined_report['payment_id'] = np.nan

	custom_combined_payment = custom_combined_report[custom_combined_report['type'] == 'payment']#.rename(columns={'amount':'credit_amount'})
	custom_combined_transfer = custom_combined_report[custom_combined_report['type'] == 'transfer']#.rename(columns={'amount':'debit_amount'})
	custom_combined_others = custom_combined_report[(custom_combined_report['type'] != 'payment') & (custom_combined_report['type'] != 'transfer')]
	custom_combined_payment['credit_amount'] = custom_combined_payment['amount']
	custom_combined_transfer['debit_amount'] = custom_combined_transfer['amount']
	custom_combined_transfer_copy = custom_combined_transfer
	#-------------------------------------------------------------------
	for i in range(len(custom_combined_payment)):
		amount = round(custom_combined_payment['credit_amount'].iloc[i], 2)
		time = custom_combined_payment['created_at'].iloc[i]
		custom_combined_transfer_extract = custom_combined_transfer_copy[custom_combined_transfer_copy['created_at'] >= time]
		break_loop = 'no'
		for ii in range(len(custom_combined_transfer_extract)):
			if break_loop == 'yes':
				break
			time2 = custom_combined_transfer_extract['created_at'].iloc[ii]
			time3 = time2 + datetime.timedelta(seconds=2)
			custom_combined_transfer_extract2 = custom_combined_transfer_extract.iloc[ii:]
			custom_combined_transfer_extract2 = custom_combined_transfer_extract2[custom_combined_transfer_extract2['created_at'] <= time3]

			single_amount = round(custom_combined_transfer_extract2['debit_amount'].iloc[0], 2)
			if single_amount == amount:
				print(i, ii)
				transfer_index_1 = custom_combined_transfer_extract2.index[0]
				custom_combined_transfer.loc[transfer_index_1, 'payment_id'] = custom_combined_payment['entity_id'].iloc[i]
				custom_combined_transfer_copy = custom_combined_transfer_copy.drop(transfer_index_1)
				break_loop = 'yes'
				break

			elif len(custom_combined_transfer_extract2) > 1:
				for iii in range(1, len(custom_combined_transfer_extract2)):
					print(i, ii, iii)
					grouping = round(custom_combined_transfer_extract2['debit_amount'].iloc[0] + custom_combined_transfer_extract2['debit_amount'].iloc[iii], 2)
					if grouping == amount:
						transfer_index_1 = custom_combined_transfer_extract2.index[0]
						transfer_index_2 = custom_combined_transfer_extract2.index[iii]
						custom_combined_transfer.loc[transfer_index_1, 'payment_id'] = custom_combined_payment['entity_id'].iloc[i]
						custom_combined_transfer.loc[transfer_index_2, 'payment_id'] = custom_combined_payment['entity_id'].iloc[i]
						custom_combined_transfer_copy = custom_combined_transfer_copy.drop(transfer_index_1)
						custom_combined_transfer_copy = custom_combined_transfer_copy.drop(transfer_index_2)
						break_loop = 'yes'
						break

	custom_combined_report = pd.concat([custom_combined_payment, custom_combined_transfer, custom_combined_others])
	custom_combined_report = custom_combined_report.sort_index()
	custom_combined_report = custom_combined_report.drop(['credit_amount', 'debit_amount'], axis=1)

	#---------------------------Trf to bank-----------------------------------------
	custom_combined_transfer = custom_combined_report[custom_combined_report['type'] == 'transfer']

	trf_to_bank = pd.read_excel(trf_to_bank)
	trf_to_bank['credit'] = trf_to_bank['credit'].round(decimals=2)

	trf_to_bank['one_second_prior'] = trf_to_bank['entity_created_at'] - datetime.timedelta(seconds=1)
	trf_to_bank['one_second_prior2'] = trf_to_bank['payment_captured_at'] - datetime.timedelta(seconds=1)

	trf_to_bank['transpose_date'] = trf_to_bank['entity_created_at'].dt.month
	trf_to_bank['transpose_month'] = trf_to_bank['entity_created_at'].dt.day
	trf_to_bank['year'] = trf_to_bank['entity_created_at'].dt.year
	trf_to_bank['hours'] = trf_to_bank['entity_created_at'].dt.hour
	trf_to_bank['minutes'] = trf_to_bank['entity_created_at'].dt.minute
	trf_to_bank['seconds'] = trf_to_bank['entity_created_at'].dt.second

	trf_to_bank['transpose_date2'] = trf_to_bank['payment_captured_at'].dt.month
	trf_to_bank['transpose_month2'] = trf_to_bank['payment_captured_at'].dt.day
	trf_to_bank['year2'] = trf_to_bank['payment_captured_at'].dt.year
	trf_to_bank['hours2'] = trf_to_bank['payment_captured_at'].dt.hour
	trf_to_bank['minutes2'] = trf_to_bank['payment_captured_at'].dt.minute
	trf_to_bank['seconds2'] = trf_to_bank['payment_captured_at'].dt.second

	trf_to_bank['transpose_date3'] = trf_to_bank['one_second_prior'].dt.month
	trf_to_bank['transpose_month3'] = trf_to_bank['one_second_prior'].dt.day
	trf_to_bank['year3'] = trf_to_bank['one_second_prior'].dt.year
	trf_to_bank['hours3'] = trf_to_bank['one_second_prior'].dt.hour
	trf_to_bank['minutes3'] = trf_to_bank['one_second_prior'].dt.minute
	trf_to_bank['seconds3'] = trf_to_bank['one_second_prior'].dt.second

	trf_to_bank['transpose_date4'] = trf_to_bank['one_second_prior2'].dt.month
	trf_to_bank['transpose_month4'] = trf_to_bank['one_second_prior2'].dt.day
	trf_to_bank['year4'] = trf_to_bank['one_second_prior2'].dt.year
	trf_to_bank['hours4'] = trf_to_bank['one_second_prior2'].dt.hour
	trf_to_bank['minutes4'] = trf_to_bank['one_second_prior2'].dt.minute
	trf_to_bank['seconds4'] = trf_to_bank['one_second_prior2'].dt.second

	trf_to_bank['corrected_date'] = np.nan
	trf_to_bank['corrected_date2'] = np.nan
	trf_to_bank['corrected_date3'] = np.nan
	trf_to_bank['corrected_date4'] = np.nan

	for i in range(len(trf_to_bank)):
		if trf_to_bank['transpose_month'].iloc[i] <= 12:
			trf_to_bank['corrected_date'].iloc[i] = datetime.datetime(trf_to_bank['year'].iloc[i], trf_to_bank['transpose_month'].iloc[i], trf_to_bank['transpose_date'].iloc[i], trf_to_bank['hours'].iloc[i], trf_to_bank['minutes'].iloc[i], trf_to_bank['seconds'].iloc[i])
			trf_to_bank['corrected_date2'].iloc[i] = datetime.datetime(trf_to_bank['year2'].iloc[i], trf_to_bank['transpose_month2'].iloc[i], trf_to_bank['transpose_date2'].iloc[i], trf_to_bank['hours2'].iloc[i], trf_to_bank['minutes2'].iloc[i], trf_to_bank['seconds2'].iloc[i])	
			trf_to_bank['corrected_date3'].iloc[i] = datetime.datetime(trf_to_bank['year3'].iloc[i], trf_to_bank['transpose_month3'].iloc[i], trf_to_bank['transpose_date3'].iloc[i], trf_to_bank['hours3'].iloc[i], trf_to_bank['minutes3'].iloc[i], trf_to_bank['seconds3'].iloc[i])	
			trf_to_bank['corrected_date4'].iloc[i] = datetime.datetime(trf_to_bank['year4'].iloc[i], trf_to_bank['transpose_month4'].iloc[i], trf_to_bank['transpose_date4'].iloc[i], trf_to_bank['hours4'].iloc[i], trf_to_bank['minutes4'].iloc[i], trf_to_bank['seconds4'].iloc[i])
		else:
			trf_to_bank['corrected_date'].iloc[i] = trf_to_bank['entity_created_at'].iloc[i]
			trf_to_bank['corrected_date2'].iloc[i] = trf_to_bank['payment_captured_at'].iloc[i]
			trf_to_bank['corrected_date3'].iloc[i] = trf_to_bank['one_second_prior'].iloc[i]
			trf_to_bank['corrected_date4'].iloc[i] = trf_to_bank['one_second_prior2'].iloc[i]

	indexer2 = recordlinkage.Index()
	indexer2.block(left_on=['credit'], right_on=['debit'])
	comparisons2 = indexer2.index(trf_to_bank, custom_combined_transfer)
	compare2 = recordlinkage.Compare()
	compare2.exact('credit', 'debit', label='Amount_Match')
	compare2.exact('entity_created_at', 'created_at', label='Date_Match')#, threshold=0.9)
	compare2.exact('payment_captured_at', 'created_at', label='Date_Match2')
	compare2.exact('one_second_prior', 'created_at', label='Date_Match3')
	compare2.exact('one_second_prior2', 'created_at', label='Date_Match4')
	compare2.exact('corrected_date', 'created_at', label='Corrected_Date_Match')
	compare2.exact('corrected_date2', 'created_at', label='Corrected_Date_Match2')
	compare2.exact('corrected_date3', 'created_at', label='Corrected_Date_Match3')
	compare2.exact('corrected_date4', 'created_at', label='Corrected_Date_Match4')
	result2 = compare2.compute(comparisons2, trf_to_bank, custom_combined_transfer)
	result_reset2 = result2.reset_index()

	result_reset2 = result_reset2.sort_values(by=['Amount_Match', 'Date_Match', 'Date_Match2', 'Date_Match3', 'Date_Match4', 'Corrected_Date_Match', 'Corrected_Date_Match2', 'Corrected_Date_Match3', 'Corrected_Date_Match4', 'level_0'], ascending=[False, False, False, False, False, False, False, False, False, True])
	result_reset2 = result_reset2[(result_reset2['Date_Match'] == 1) | (result_reset2['Date_Match2'] == 1) | (result_reset2['Date_Match3'] == 1) | (result_reset2['Date_Match4'] == 1) | (result_reset2['Corrected_Date_Match'] == 1) | (result_reset2['Corrected_Date_Match2'] == 1) | (result_reset2['Corrected_Date_Match3'] == 1) | (result_reset2['Corrected_Date_Match4'] == 1)]

	result_reset2 = result_reset2.merge(custom_combined_transfer[['payment_id']], left_on='level_1', right_index=True, how='left')

	trf_to_bank = trf_to_bank.iloc[:, :17]
	trf_to_bank['payment_id'] = np.nan
	while len(result_reset2) > 0:
		trf_to_bank.loc[result_reset2['level_0'].iloc[0], 'payment_id'] = result_reset2['payment_id'].iloc[0]
		result_reset2 = result_reset2[(result_reset2['level_0'] != result_reset2['level_0'].iloc[0]) & (result_reset2['level_1'] != result_reset2['level_1'].iloc[0])]

	writer = pd.ExcelWriter('kodo_reconciliation.xlsx')
	custom_combined_report['payment_id'] = np.where((custom_combined_report['payment_id'].isnull()) & (custom_combined_report['type'] == 'transfer'), 'Not Found', custom_combined_report['payment_id'])
	custom_combined_report.to_excel(writer, sheet_name='Custom Combined Report', index=False)
	trf_to_bank.to_excel(writer, sheet_name='Trf to Bank', index=False)
	
	workbook = writer.book
	number_format = workbook.add_format({'num_format': '#,##0'})
	fail_format = workbook.add_format({'bg_color': '#FFC7CE', 'font_color': '#9C0006'})
	pass_format = workbook.add_format({'bg_color': '#C6EFCE', 'font_color': '#006100'})
	left_format = workbook.add_format()
	left_format.set_align('left')
	center_format = workbook.add_format()
	center_format.set_align('center')

	sheet1 = writer.sheets['Custom Combined Report']
	sheet2 = writer.sheets['Trf to Bank']

	sheet1.conditional_format('N2:N'+str(len(custom_combined_report)+1), {'type': 'text', 'criteria': 'containing', 'value': 'pay_', 'format': pass_format})
	sheet1.conditional_format('N2:N'+str(len(custom_combined_report)+1), {'type': 'text', 'criteria': 'containing', 'value': 'Not Found', 'format': fail_format})

	sheet2.conditional_format('R2:R'+str(len(trf_to_bank)+1), {'type': 'text', 'criteria': 'containing', 'value': 'pay_', 'format': pass_format})
	sheet2.conditional_format('R2:R'+str(len(trf_to_bank)+1), {'type': 'text', 'criteria': 'not containing', 'value': 'pay_', 'format': fail_format})
	
	sheet1.set_column('A:A', 25, left_format)
	sheet1.set_column('B:B', 10, left_format)
	sheet1.set_column('C:E', 10, number_format)
	sheet1.set_column('F:F', 10, center_format)
	sheet1.set_column('G:J', 10, number_format)
	sheet1.set_column('K:K', 25, center_format)
	sheet1.set_column('L:M', 10, center_format)
	sheet1.set_column('N:N', 25, center_format)

	sheet2.set_column('A:B', 25, left_format)
	sheet2.set_column('C:C', 10, number_format)
	sheet2.set_column('D:D', 10, center_format)
	sheet2.set_column('E:H', 10, number_format)
	sheet2.set_column('I:L', 10, center_format)
	sheet2.set_column('M:R', 25, center_format)

	writer.save()

	return