import streamlit as st
import numpy as np
import pandas as pd
from PIL import Image
import time

st.title('基礎')

st.write('DateFrame')

option = st.selectbox(
    'あなたの好きな数字を教えてください',
    list(range(1,11))
)

'あなたの好きな数字は', option , 'です！'

# if st.checkbox('show image'):
#     img = Image.open('Wallpaper_PokemonSV_B_1920_1080.jpg')
#     st.image(img, caption='Pokemon', use_column_width=True)

# df = pd.DataFrame(
#     np.random.rand(100, 2),
#     columns=['lat', 'lon']
# )

# st.line_chart(df)