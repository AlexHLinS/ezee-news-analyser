

'''
# Block 1
primary_source_url = Column(String) # с антиплагиата
created_at = Column(DATETIME) # первоисточник с антиплагиата
text = Column(String) # текст
source_score = Column(Float) # считать не надо
times_published = Column(Integer) # кол-во источников
percentage_blacklist = Column(Float) #
avg_sources_score = Column(Float)
reliable_sources_flag = Column(Boolean)

# Block 2
diagram_data = Column(String) Нужны все источники и дата создания всех статей

# Block 3
plagiary_percentage = Column(Float)
is_any_sentiment_delta = Column(Boolean)
facts = Column(String)

# Block 4
grammatic_errors_count = Column(Integer)
spam_index = Column(Float)
water_index = Column(Float)
sentiment_index = Column(Float)
speech_index = Column(Float)
intuition_index = Column(Float)
clickbait_index = Column(Float)
rationality_index = Column(Float)
fake_index = Column(Float)

'''