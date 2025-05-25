import scrapy

class Phase1DataItem(scrapy.Item):
    """Phase 1 focused data item - only three specific data points"""
    municipality = scrapy.Field()
    municipality_org_number = scrapy.Field()
    
    # The three required data points for Phase 1
    timtaxa_livsmedel = scrapy.Field()      # Hourly rate for food control (e.g., 1350)
    debitering_livsmedel = scrapy.Field()   # Billing model: 'förskott' or 'efterhand'
    timtaxa_bygglov = scrapy.Field()        # Hourly rate for building permits (e.g., 1200)
    
    # Quality indicators for timtaxa fields
    timtaxa_livsmedel_quality = scrapy.Field()    # 'typical', 'low', 'high'
    timtaxa_bygglov_quality = scrapy.Field()      # 'typical', 'low', 'high'
    debitering_livsmedel_original = scrapy.Field()  # Original value before normalization
    
    # Metadata
    source_url = scrapy.Field()
    source_type = scrapy.Field()            # 'PDF' or 'HTML'
    extraction_date = scrapy.Field()
    extraction_method = scrapy.Field()
    confidence = scrapy.Field()
    
    # Enhanced validation metadata
    validation_warnings = scrapy.Field()
    validation_date = scrapy.Field()
    validation_version = scrapy.Field()
    data_completeness = scrapy.Field()      # How many of the 3 fields were found
    completeness_score = scrapy.Field()     # 0-1 score
    data_quality = scrapy.Field()           # 0-100 quality score
    status = scrapy.Field()                 # 'complete', 'partial', 'empty'
    phase1_fields_found = scrapy.Field()    # Number of Phase 1 fields found
    phase1_success_rate = scrapy.Field()    # Success rate for this item

# Keep the original for backward compatibility if needed
class SwedishMunicipalFeeItem(scrapy.Item):
    """Original comprehensive fee item (deprecated for Phase 1)"""
    municipality = scrapy.Field()
    municipality_org_number = scrapy.Field()
    fee_name = scrapy.Field()
    amount = scrapy.Field()
    currency = scrapy.Field()
    unit = scrapy.Field()
    category = scrapy.Field()
    description = scrapy.Field()
    source_url = scrapy.Field()
    source_type = scrapy.Field()
    extraction_method = scrapy.Field()
    extraction_date = scrapy.Field()
    cms_type = scrapy.Field()
    municipality_type = scrapy.Field()
    confidence = scrapy.Field()
    context = scrapy.Field()
    element_info = scrapy.Field()
    
    # Enhanced validation metadata
    validation = scrapy.Field()
    quality = scrapy.Field()
    
    # Bygglov specific fields
    bygglov_type = scrapy.Field()
    area_based = scrapy.Field()
    pbb_based = scrapy.Field()
    area_range = scrapy.Field()
    pbb_multiplier = scrapy.Field()

    # Additional fields for specific fee types
    effective_date = scrapy.Field()
    expiry_date = scrapy.Field()
    legal_reference = scrapy.Field()
    contact_info = scrapy.Field() 