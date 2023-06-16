#!/usr/bin/env python
# coding: utf-8

# In[1]:


# DB

import streamlit as st
import sqlite3
import pandas as pd

conn = sqlite3.connect('data.db')
c = conn.cursor()

# Functions

def create_table():
	c.execute('CREATE TABLE IF NOT EXISTS blogtable(author TEXT,title TEXT,link TEXT,postdate DATE)')

def add_data(author,title,link,postdate):
	c.execute('INSERT INTO blogtable(author,title,link,postdate) VALUES (?,?,?,?)',(author,title,link,postdate))
	conn.commit()

def view_all_notes():
	c.execute('SELECT * FROM blogtable ORDER by postdate desc')
	data = c.fetchall()
	return data

def view_all_titles():
	c.execute('SELECT DISTINCT title FROM blogtable')
	data = c.fetchall()
	return data

def get_blog_by_title(title):
	c.execute('SELECT * FROM blogtable WHERE title="{}"'.format(title))
	data = c.fetchall()
	return data

def get_blog_by_author(author):
	c.execute('SELECT * FROM blogtable WHERE author="{}"'.format(author))
	data = c.fetchall()
	return data

def delete_data(title):
	c.execute('DELETE FROM blogtable WHERE title="{}"'.format(title))
	conn.commit()


# In[2]:


# Layout Templates
html_temp = """
<div style="background-color:{};padding:10px;border-radius:10px">
<h1 style="color:{};text-align:center;">西墙网科技头条</h1>
</div>
"""
title_temp ="""
<div style="background-color:#ffffff;padding:0px;border-radius:0px;margin:0px;">
<p style="text-align:left">{} by {} {}</p>
</div>
"""
link_temp ="""
<div style="background-color:#464e5f;padding:10px;border-radius:5px;margin:10px;">
<h4 style="color:white;text-align:center;">{}</h1>
<h6>Author:{}</h6> 
<h6>Post Date: {}</h6>
<img src="https://www.w3schools.com/howto/img_avatar.png" alt="Avatar" style="vertical-align: middle;width: 50px;height: 50px;border-radius: 50%;" >
<br/>
<br/>
<p style="text-align:justify">{}</p>
</div>
"""
head_message_temp ="""
<div style="background-color:#464e5f;padding:10px;border-radius:5px;margin:10px;">
<h4 style="color:white;text-align:center;">{}</h1>
<img src="https://www.w3schools.com/howto/img_avatar.png" alt="Avatar" style="vertical-align: middle;float:left;width: 50px;height: 50px;border-radius: 50%;">
<h6>Author:{}</h6> 
<h6>Post Date: {}</h6> 
</div>
"""
full_message_temp ="""
<div style="background-color:silver;overflow-x: auto; padding:10px;border-radius:5px;margin:10px;">
<p style="text-align:justify;color:black;padding:10px">{}</p>
</div>
"""


# In[3]:


def main():
	"""A Simple CRUD  Blog"""
	
	st.markdown(html_temp.format('royalblue','white'),unsafe_allow_html=True)

	menu = ["Home","Share Your Link","Search","Manage Blog"]
	choice = st.sidebar.selectbox("Menu",menu)

	if choice == "Home":
		st.subheader("Home")
		result = view_all_notes()
		
		for i in result:
			b_author = i[0]
			b_title = i[1]
			b_link = str(i[2])
			b_post_date = i[3]
			alink = f'<a target="_blank" href="{b_link}">{b_title}</a>'
			st.markdown(title_temp.format(alink,b_author,b_post_date),unsafe_allow_html=True)

	elif choice == "Share Your Link":
		st.subheader("Add Your Link")
		create_table()
		blog_author = st.text_input("Enter Your Name",max_chars=10)
		blog_title = st.text_input("Enter a Title")
		blog_link = st.text_area("Enter http or https Link Here",height=200)
		blog_post_date = st.date_input("Date")
		if st.button("Add"):
			add_data(blog_author,blog_title,blog_link,blog_post_date)
			st.success("Link:{} saved".format(blog_title))	

	elif choice == "Search":
		st.subheader("Search links")
		search_term = st.text_input('Enter Search Term')
		search_choice = st.radio("Field to Search By",("title","author"))
		
		if st.button("Search"):

			if search_choice == "title":
				link_result = get_blog_by_title(search_term)
			elif search_choice == "author":
				link_result = get_blog_by_author(search_term)

			for i in link_result:
				b_author = i[0]
				b_title = i[1]
				b_link = i[2]
				b_post_date = i[3]
				st.text("Reading Time:{}".format(readingTime(b_link)))
				st.markdown(head_message_temp.format(b_title,b_author,b_post_date),unsafe_allow_html=True)
				st.markdown(full_message_temp.format(b_link),unsafe_allow_html=True)

	elif choice == "Manage Blog":
		st.subheader("Manage links")

		result = view_all_notes()
		clean_db = pd.DataFrame(result,columns=["Author","Title","Links","Post Date"])
		st.dataframe(clean_db)

		unique_titles = [i[0] for i in view_all_titles()]
		delete_blog_by_title = st.selectbox("Unique Title",unique_titles)
		new_df = clean_db
		if st.button("Delete"):
			delete_data(delete_blog_by_title)
			st.warning("Deleted: '{}'".format(delete_blog_by_title))

if __name__ == '__main__':
	main()

