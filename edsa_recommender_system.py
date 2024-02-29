"""

    Streamlit webserver-based Recommender Engine.

    Author: Explore Data Science Academy.

    Note:
    ---------------------------------------------------------------------
    Please follow the instructions provided within the README.md file
    located within the root of this repository for guidance on how to use
    this script correctly.

    NB: !! Do not remove/modify the code delimited by dashes !!

    This application is intended to be partly marked in an automated manner.
    Altering delimited code may result in a mark of 0.
    ---------------------------------------------------------------------

    Description: This file is used to launch a minimal streamlit web
	application. You are expected to extend certain aspects of this script
    and its dependencies as part of your predict project.

	For further help with the Streamlit framework, see:

	https://docs.streamlit.io/en/latest/

"""
# Streamlit dependencies
import streamlit as st

# Data handling dependencies
import pandas as pd
import numpy as np

# Custom Libraries
from utils.data_loader import load_movie_titles
from recommenders.collaborative_based import collab_model
from recommenders.content_based import content_model

# Data Loading
title_list = load_movie_titles('resources/data/movies.csv')

# App declaration
def main():

    # DO NOT REMOVE the 'Recommender System' option below, however,
    # you are welcome to add more options to enrich your app.
    page_options = ["Welcome","About","EDA","Recommender System","Search for a movie","Solution Overview","Reviews","Trailers"]

    # -------------------------------------------------------------------
    # ----------- !! THIS CODE MUST NOT BE ALTERED !! -------------------
    # -------------------------------------------------------------------
    page_selection = st.sidebar.selectbox("Choose Option", page_options)
    if page_selection == "Recommender System":
        # Header contents
        st.write('#CineSuggest')
        st.write('### Where Movies Meet Your Mood')
        st.image('resources/imgs/Image_header.png',use_column_width=True)
        # Recommender System algorithm selection
        sys = st.radio("Select an algorithm", ('Content Based Filtering', 'Collaborative Based Filtering'))

        # User-based preferences
        st.write('### Enter Your Three Favorite Movies')
        movie_1 = st.selectbox('Fisrt Option',title_list[14930:15200])
        movie_2 = st.selectbox('Second Option',title_list[25055:25255])
        movie_3 = st.selectbox('Third Option',title_list[21100:21200])
        fav_movies = [movie_1,movie_2,movie_3]

        # Perform top-10 movie recommendation generation
        
        if st.button("Recommend"):
            try:
                with st.spinner('Processing data...'):
                    if sys == 'Content Based Filtering':
                        top_recommendations = content_model(movie_list=fav_movies, top_n=10)
                    elif sys == 'Collaborative Based Filtering':
                        top_recommendations = collab_model(movie_list=fav_movies, top_n=10)

                top_recommendations_list = top_recommendations.tolist() if isinstance(top_recommendations, pd.Series) else top_recommendations

                st.title("We think you'll like:")  
                for i, movie_title in enumerate(top_recommendations_list):
                    st.subheader(f"{i + 1}. {movie_title}")
            except Exception as e:
                st.error(f"Oops! An error occurred: {str(e)}")


    # -------------------------------------------------------------------

    # ------------- SAFE FOR ALTERING/EXTENSION -------------------
    if page_selection == "Search for a movie":
        st.title("Search for Movies")
        
        st.image('resources/imgs/movie1.jpg', use_column_width=True)
        st.markdown(' Our goal is to provide you with a curated and personalized movie-watching experience based on sophisticated algorithms that analyze your viewing history and preferences. ', unsafe_allow_html=True)
        st.markdown(' If, however, you prefer a different approach or choose not to use our recommender system, we offer an alternative method. Utilize our filtering options to tailor your movie selection based on two key criteria: ', unsafe_allow_html=True)
        st.markdown(' 1. Rating: Filter movies based on user ratings to ensure you discover films highly regarded by fellow viewers. ', unsafe_allow_html=True)
        st.markdown(' 2. Year of Release: Customize your movie choices by selecting a specific year or range of years, allowing you to explore cinematic offerings from a particular era.', unsafe_allow_html=True)
        st.markdown(' 3. Genre: Narrow down your options by choosing genres that align with your current mood or taste, from action-packed adventures to heartwarming dramas. ', unsafe_allow_html=True)
        st.markdown(" We're committed to providing you with a diverse and enjoyable movie-watching experience. Enjoy exploring and discovering your next favorite film! ", unsafe_allow_html=True)
        # Movies
        df = pd.read_csv('resources/data/movies.csv')
        rating = pd.read_csv('resources/data/ratings.csv')
        
        def explode(df, lst_cols, fill_value='', preserve_index=False):
            import numpy as np
             # make sure `lst_cols` is list-alike
            if (lst_cols is not None
                    and len(lst_cols) > 0
                    and not isinstance(lst_cols, (list, tuple, np.ndarray, pd.Series))):
                lst_cols = [lst_cols]
            # all columns except `lst_cols`
            idx_cols = df.columns.difference(lst_cols)
            # calculate lengths of lists
            lens = df[lst_cols[0]].str.len()
            # preserve original index values    
            idx = np.repeat(df.index.values, lens)
            # create "exploded" DF
            res = (pd.DataFrame({
                        col:np.repeat(df[col].values, lens)
                        for col in idx_cols},
                        index=idx)
                    .assign(**{col:np.concatenate(df.loc[lens>0, col].values)
                            for col in lst_cols}))
            # append those rows that have empty lists
            if (lens == 0).any():
                # at least one list in cells is empty
                res = (res.append(df.loc[lens==0, idx_cols], sort=False)
                            .fillna(fill_value))
            # revert the original index order
            res = res.sort_index()   
            # reset index if requested
            if not preserve_index:        
                res = res.reset_index(drop=True)
            return res 
        movie_data = pd.merge(rating, df, on='movieId')
        movie_data['year'] = movie_data.title.str.extract('(\(\d\d\d\d\))',expand=False)
        #Removing the parentheses
        movie_data['year'] = movie_data.year.str.extract('(\d\d\d\d)',expand=False)

        movie_data.genres = movie_data.genres.str.split('|')
        movie_rating = st.sidebar.number_input("Pick a rating ",0.5,5.0, step=0.5)

        movie_data = explode(movie_data, ['genres'])
        movie_title = movie_data['genres'].unique()
        title = st.selectbox('Genre', movie_title)
        movie_data['year'].dropna(inplace = True)
        movie_data = movie_data.drop(['movieId','timestamp','userId'], axis = 1)
        year_of_movie_release = movie_data['year'].sort_values(ascending=False).unique()
        release_year = st.selectbox('Year', year_of_movie_release)

        movie = movie_data[(movie_data.rating == movie_rating)&(movie_data.genres == title)&(movie_data.year == release_year)]
        df = movie.drop_duplicates(subset = ["title"])
        if len(df) !=0:
            st.write(df)
        if len(df) ==0:
            st.write('We have no movies for that rating!')        
        def youtube_link(title):
    
            """This function takes in the title of a movie and returns a Search query link to youtube
    
            INPUT: ('Avengers age of ultron')
            -----------
    
            OUTPUT: https://www.youtube.com/results?search_query=The+little+Mermaid&page=1
            ----------
            """
            title = title.replace(' ','+')
            base = "https://www.youtube.com/results?search_query="
            q = title
            page = "&page=1"
            URL = base + q + page
            return URL            
        if len(df) !=0:           
            for _, row in df.iterrows():
                st.write(row['title'])
                st.write(youtube_link(title = row['title']))

    if page_selection == "Welcome":
        st.title('CineSuggest ')
        st.image('resources/imgs/cinesuggestLogo.jpg', use_column_width=True)
        st.write('## *** Your Personalized Movie Journey Begins Here! ***')

    if page_selection == 'About':
        st.title("About")
        st.markdown("At CineSuggest, we believe that the world of cinema is a vast and thrilling tapestry waiting to be explored. Our mission is to enhance your movie-watching experience by providing personalized, handpicked recommendations tailored just for you.")
        st.image("resources/imgs/cinema.jpg",use_column_width=True)
        st.subheader("What sets us apart?")
        st.markdown("CineSuggest is not just another movie recommendation app; it's your dedicated companion on a cinematic journey. Our team of passionate film enthusiasts and AI experts has meticulously crafted an algorithm that understands your unique tastes, preferences, and moods. We go beyond generic suggestions, ensuring that every movie recommendation feels like a personalized gem.")
        st.subheader("How The App Works")
        st.markdown("With just a few clicks, you're on your way to discovering your next favorite movie. Select three of your most cherished films from our extensive database, and let our intelligent algorithm work its magic. We analyze your choices to predict your preferences, curating a personalized list of the top 10 movies you are most likely to enjoy.")
        st.subheader("Data Visualizations for Movie Enthusiasts")
        st.markdown("Dive deeper into the world of cinema with our data visualizations. Explore word clouds showcasing the most popular words in movie titles and plots across various genres. Uncover trends, discover common themes, and gain insights into the diverse cinematic landscape.")
        st.subheader("Embark on your cinematic journey with CineSuggest - where the magic of movies meets personalized recommendations.")

    
    if page_selection == 'EDA':
        st.title('Exploratoring The Relationships')
        st.image('./resources/imgs/plot1.png', use_column_width=True)
        st.markdown('Stargate, the (1994) is the movie that was rated the most by users and pulp fiction (1994) has been the worst rated movies.')
        st.markdown('--------')  
    
        st.image('./resources/imgs/plot2.png', use_column_width=True)
        st.markdown('Insights the rating are left-skewed which')
        st.markdown('The mean and median values are very close to round 3.5')
        st.markdown('The most common rating is 4')
        st.markdown('--------')

        st.image('./resources/imgs/plot3.png', use_column_width=True)
        st.markdown('Shawshank Redemption, the (1994) is the movie that was rated the most by users and pulp fiction (1994) has been the most rated movies.')
        st.markdown('--------')

        st.image('./resources/imgs/plot4.png', use_column_width=True)
        st.markdown('A High-count number of genres in drama and a low count number in film-Noir and IMAX')
        st.markdown('--------')

       
   
    if page_selection == "Solution Overview":
        st.title("Solution Overview")
        st.markdown("### CONTENT BASED FILTERING")
        st.image('./resources/imgs/content base.png', use_column_width=True)
        st.markdown('Uses item features to recommend other items similar to what the user likes, based on their previous actions or explicit feedback.')
        

        st.markdown('### COLLABORATIVE BASED FILTERING')
        st.image('./resources/imgs/collaborative.png', use_column_width=True)
        st.markdown('builds a model from your past behavior (i.e. movies watched or selected by the you) as well as similar decisions made by other users.')
        


    if page_selection == 'Reviews':
        st.title("Get in touch with us")
        st.markdown('''<span style="skyblue"> **Help us improve this app by rating it. Tell us how to give you a better user experience.** </span>''', unsafe_allow_html=True)
        @st.cache(allow_output_mutation=True)
        def get_data():
            return []
        name = st.text_input("User name")
        inputs = st.text_input("Let us improve your user experience")
        rate = st.slider("Rate us", 0, 5)
        if st.button("Submit"):
            get_data().append({"User name": name, "Suggestion": inputs,"rating":rate})
        
        st.markdown('''<span style="color:blue"> **For any questions contact us here:** </span>''', unsafe_allow_html=True)
        st.markdown('reviews@cineintelectinsights.com')


    if page_selection == "Trailers":
        st.title('CineSuggest Movie Trailers ')
        video_url = "https://www.youtube.com/watch?v=gBHde1DVp5c"
        st.video(video_url)
        st.write('## *** Your Personalized Movie Journey Begins Here! ***')


if __name__ == '__main__':
    main()
