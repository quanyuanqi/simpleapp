#!/usr/bin/env python
# coding: utf-8


# DB


import streamlit as st
import sqlite3
import pandas as pd

# Security

import hashlib
def make_hashes(password):
	return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password,hashed_text):
	if make_hashes(password) == hashed_text:
		return hashed_text
	return False

conn = sqlite3.connect('data.db')
c = conn.cursor()

# Functions

def create_table():
	c.execute('CREATE TABLE IF NOT EXISTS blogtable(username TEXT,title TEXT,link TEXT,postdate DATE)')

def add_data(username,title,link,postdate):
	c.execute('INSERT INTO blogtable(username,title,link,postdate) VALUES (?,?,?,?)',(username,title,link,postdate))
	conn.commit()

def view_all_notes():
	c.execute('SELECT * FROM blogtable ORDER by postdate desc')
	data = c.fetchall()
	return data

def view_user_notes(username):
	c.execute('SELECT * FROM blogtable WHERE username = ? ORDER by postdate desc' , (username,))
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

def get_blog_by_username(username):
	c.execute('SELECT * FROM blogtable WHERE username="{}"'.format(username))
	data = c.fetchall()
	return data

def delete_data(title):
	c.execute('DELETE FROM blogtable WHERE title="{}"'.format(title))
	conn.commit()

def create_usertable():
	c.execute('CREATE TABLE IF NOT EXISTS userstable(username TEXT,password TEXT)')

def add_userdata(username,password):
	c.execute('INSERT INTO userstable(username,password) VALUES (?,?)',(username,password))
	conn.commit()

def login_user(username,password):
	c.execute('SELECT * FROM userstable WHERE username =? AND password = ?',(username,password))
	data = c.fetchall()
	return data

def view_username_password(username):
	c.execute("SELECT password FROM userstable WHERE username = ?", (username,))
	password = c.fetchone()
	if password:
		return password[0]
	else:
		return "Something wrong."

# Layout Templates

html_temp = """
<div style="background-color:{};padding:10px;border-radius:10px">
<h1 style="color:{};text-align:center;">Tech Headlines Shared</h1>
</div>
"""
title_temp ="""
<div style="background-color:#ffffff;padding:0px;border-radius:0px;margin:0px;">
<p style="text-align:left">{} by {} {}</p>
</div>
"""

head_message_temp ="""
<div style="background-color:#464e5f;padding:10px;border-radius:5px;margin:10px;">
<h4 style="color:white;text-align:center;">{}</h1>
<img src="https://www.w3schools.com/howto/img_avatar.png" alt="Avatar" style="vertical-align: middle;float:left;width: 50px;height: 50px;border-radius: 50%;">
<h6>username:{}</h6> 
<h6>Post Date: {}</h6> 
</div>
"""
full_message_temp ="""
<div style="background-color:silver;overflow-x: auto; padding:10px;border-radius:5px;margin:10px;">
<p style="text-align:justify;color:black;padding:10px">{}</p>
</div>
"""

def main():
	"""A Simple Reddit-Style Web App"""
	
	st.markdown(html_temp.format('royalblue','white'),unsafe_allow_html=True)

	menu = ["Home","Search","Login","SignUp"]
	choice = st.sidebar.selectbox("Menu",menu)

	if choice == "Home":
		st.subheader("Home")
		result = view_all_notes()
		
		for i in result:
			b_username = i[0]
			b_title = i[1]
			b_link = str(i[2])
			b_post_date = i[3]
			alink = f'<a target="_blank" href="{b_link}">{b_title}</a>'
			st.markdown(title_temp.format(alink,b_username,b_post_date),unsafe_allow_html=True)

	elif choice == "Search":
		st.subheader("Search links")
		search_term = st.text_input('Enter Search Term')
		search_choice = st.radio("Field to Search By",("title","username"))
		
		if st.button("Search"):

			if search_choice == "title":
				link_result = get_blog_by_title(search_term)
			elif search_choice == "username":
				link_result = get_blog_by_username(search_term)

			for i in link_result:
				b_username = i[0]
				b_title = i[1]
				b_link = i[2]
				b_post_date = i[3]
				st.text("Reading Time:{}".format(readingTime(b_link)))
				st.markdown(head_message_temp.format(b_title,b_username,b_post_date),unsafe_allow_html=True)
				st.markdown(full_message_temp.format(b_link),unsafe_allow_html=True)

	elif choice == "Login":
		st.subheader("Login Section")
		username = st.sidebar.text_input("User Name")
		password = st.sidebar.text_input("Password",type='password')
		if st.sidebar.checkbox("Login"):
			create_usertable()
			hashed_pswd = make_hashes(password)

			result = login_user(username,check_hashes(password,hashed_pswd))
			
			if result:
				st.success("Logged In as {}".format(username))
				task = st.selectbox("Task",["Add Post","Manage Links","Profiles"])
				if task == "Add Post":
					st.subheader("Add Your Link")
					create_table()
					blog_username = st.text_input("Enter Your Name",max_chars=10)
					blog_title = st.text_input("Enter a Title")
					blog_link = st.text_area("Enter http or https Link Here",height=200)
					blog_post_date = st.date_input("Date")
					if st.button("Add"):
						add_data(blog_username,blog_title,blog_link,blog_post_date)
						st.success("Link:{} saved".format(blog_title))

				elif task == "Manage Links":
					st.subheader("Manage My Links")
					result = view_user_notes(username)
					clean_db = pd.DataFrame(result,columns=["Username","Title","Links","Post Date"])
					st.dataframe(clean_db)

					unique_titles = [i[1] for i in result]
					delete_blog_by_title = st.selectbox("Unique Title",unique_titles)
					if st.button("Delete"):
						delete_data(delete_blog_by_title)
						st.warning("Deleted: '{}'".format(delete_blog_by_title))
					
				elif task == "Profiles":
					st.subheader("User Profiles")
					user_result = view_username_password(username)
					clean_db = pd.DataFrame([user_result], columns=["Password"])
					clean_db["Username"] = username
					clean_db = clean_db[["Username", "Password"]]
					st.dataframe(clean_db)

			else:
				st.warning("Incorrect Username/Password")


	elif choice == "SignUp":
		st.subheader("Create New Account")
		new_user = st.text_input("Username")
		new_password = st.text_input("Password",type='password')

		if st.button("Signup"):
			create_usertable()
			add_userdata(new_user,make_hashes(new_password))
			st.success("You have successfully created a valid Account")
			st.info("Go to Login Menu to login")


if __name__ == '__main__':
	main()
