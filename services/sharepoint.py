import requests
import streamlit as st

AUTHORIZATION_TOKEN = st.secrets.get("SHAREPOINT_AUTHORIZATION_TOKEN", "")

def search_sharepoint(query):
    cookies = {
        'MUID': '015F7DAA57F36BC010D368C656F56AE2',
    }
    headers = {
        'accept': 'application/json',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'authorization': f'Bearer {AUTHORIZATION_TOKEN}',
        'content-type': 'application/json',
        'origin': 'https://substrate.office.com',
        'priority': 'u=1, i',
        'referer': 'https://substrate.office.com/search/api/v2/resources',
        'sec-ch-ua': '"Not;A=Brand";v="99", "Google Chrome";v="139", "Chromium";v="139"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-storage-access': 'active',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36',
        'x-anchormailbox': 'PUID:1003200427516B9B@d5f1622b-14a3-45a6-b069-003f8dc4851f',
        'x-client-flights': 'EnableConnectorsInterleavingGA,EnableClientContextIn3S,UseAdaptiveCardTemplates,EnableSPCustomizationInCustomVertical',
        'x-client-language': 'en-us',
        'x-client-localtime': '2025-10-22T19:03:37.575+05:30',
        'x-client-version': '1.20251015.4.0',
        'x-routingparameter-sessionkey': 'PUID:1003200427516B9B@d5f1622b-14a3-45a6-b069-003f8dc4851f',
        # 'cookie': 'MUID=015F7DAA57F36BC010D368C656F56AE2',
    }
    params = {
        'setFlight': 'querymicroservice,SingleCallRequest,EnableServerSideWholePageRelevance,ResultClusterArbitration',
        'msgRequestId': 'b1c608c9-0425-46c4-ad49-c7c1322d0508',
    }

    json_data = {
        'AnswerEntityRequests': [
            {
                'Query': {
                    'QueryString': f'{query}',
                },
                'EntityTypes': [
                    'Building',
                    'EditorialQnA',
                    'Bookmark',
                    'Acronym',
                    'External',
                    'TuringQnA',
                    'Topic',
                ],
                'From': 0,
                'Size': 10,
                'SupportedResultSourceFormats': [
                    'AdaptiveCard',
                    'EntityData',
                    'AdaptiveCardTemplateBinding',
                ],
                'PreferredResultSourceFormat': 'AdaptiveCard',
                'EnableAsyncResolution': True,
            },
        ],
        'EntityRequests': [
            {
                'EntityType': 'File',
                'ContentSources': [
                    'SharePoint',
                    'OneDriveBusiness',
                ],
                'Fields': [
                    '.callerStack',
                    '.correlationId',
                    '.mediaBaseUrl',
                    '.spResourceUrl',
                    '.thumbnailUrl',
                    'AuthorOWSUSER',
                    'ContainerTypeId',
                    'ContentClass',
                    'ContentTypeId',
                    'Created',
                    'DefaultEncodingURL',
                    'DepartmentId',
                    'Description',
                    'DocId',
                    'EditorOWSUSER',
                    'FileExtension',
                    'FileType',
                    'Filename',
                    'GeoLocationSource',
                    'HitHighlightedSummary',
                    'IsContainer',
                    'IsHubSite',
                    'LastModifiedTime',
                    'LinkingUrl',
                    'ListID',
                    'ModifiedBy',
                    'MediaDuration',
                    'ParentLink',
                    'Path',
                    'PiSearchResultId',
                    'PictureThumbnailURL',
                    'ProgID',
                    'PromotedState',
                    'RelatedHubSites',
                    'SPWebUrl',
                    'SecondaryFileExtension',
                    'ServerRedirectedPreviewURL',
                    'ServerRedirectedUrl',
                    'ShortcutUrl',
                    'SiteId',
                    'SiteLogo',
                    'SiteTemplateId',
                    'SiteTitle',
                    'Title',
                    'UniqueID',
                    'UniqueId',
                    'ViewCount',
                    'ViewsLifeTimeUniqueUsers',
                    'WebId',
                    'isDocument',
                    'isexternalcontent',
                    'ListTemplateTypeId',
                    'IsArchivedAtFileLevel',
                    'PrivacyIndicator',
                    'ColorHex',
                    'ModifierUPNs',
                    'InformationProtectionLabelId',
                    'SiteSensitivityLabelID',
                ],
                'Query': {
                    'QueryString': f'{query}',
                    'DisplayQueryString': f'{query}',
                    'QueryTemplate': '({searchterms}) (NOT ContentClass:ExternalLink AND NOT FileExtension:vtt AND NOT (Title:OneNote_DeletedPages OR Title:OneNote_RecycleBin) AND NOT SecondaryFileExtension:onetoc2 AND NOT (ContentClass:STS_List_544 OR ContentClass:STS_ListItem_544) AND NOT WebTemplate:SPSPERS AND NOT (ContentClass:STS_Site AND SiteTemplateId:21) AND NOT (ContentClass:STS_Site AND SiteTemplateId:22) AND NOT (ContentClass:STS_List_DocumentLibrary AND SiteTemplateId:21) AND NOT (ContentClass:STS_List_DocumentLibrary AND Author:"system account")) AND (SPTranslationLanguage:en-us OR (NOT SPTranslatedLanguages:en-us AND NOT SPIsTranslation:true)) NOT ContentClass:"STS_ListItem_UserInformation"',
                },
                'Sort': [
                    {
                        'Field': 'PersonalScore',
                        'SortDirection': 'Desc',
                    },
                ],
                'EnableQueryUnderstanding': False,
                'EnableSpeller': False,
                'IdFormat': 0,
                'PreferredResultSourceFormat': 'AdaptiveCardTemplateBinding',
                'EnableResultAnnotations': True,
                'ResultsMerge': {
                    'Type': 'Interleaved',
                },
                'FederationContext': {
                    'SpoFederationContext': {
                        'UserContextUrl': 'https://secureservernet-my.sharepoint.com/personal/pankaj1_godaddy_com/',
                    },
                },
                'ExtendedQueries': [
                    {
                        'SearchProvider': 'SharePoint',
                        'Query': {
                            'Culture': 1033,
                            'EnableQueryRules': False,
                            'EnableMultiGeo': True,
                            'TrimDuplicates': False,
                            'BypassResultTypes': True,
                            'ProcessBestBets': False,
                            'ProcessPersonalFavorites': False,
                            'EnableInterleaving': False,
                            'SourceId': '8413CD39-2156-4E00-B54D-11EFD9ABDB89',
                            'TimeSpanToUTC': '05:30',
                        },
                    },
                ],
                'HitHighlight': {
                    'HitHighlightedProperties': [
                        'HitHighlightedSummary',
                    ],
                    'SummaryLength': 200,
                },
            },
        ],
        'Cvid': '2697425a-5150-45b0-be9e-bb81b7b2da51',
        'LogicalId': '5e4fe1db-bd38-4bc1-88ac-121d71ad6dd2',
        'Culture': 'en-us',
        'UICulture': 'en-us',
        'TimeZone': 'UTC',
        'TextDecorations': 'Off',
        'Scenario': {
            'Name': 'SPHomeWeb',
            'Dimensions': [
                {
                    'DimensionName': 'QueryType',
                    'DimensionValue': 'AllResults',
                },
                {
                    'DimensionName': 'FormFactor',
                    'DimensionValue': 'Web',
                },
            ],
        },
        'QueryAlterationOptions': {
            'EnableSuggestion': True,
            'EnableAlteration': True,
            'SupportedRecourseDisplayTypes': [
                'ServiceSideRecourseLink',
            ],
        },
        'WholePageRankingOptions': {
            'EnableEnrichedRanking': True,
            'EnableLayoutHints': True,
            'SupportedSerpRegions': [
                'MainLine',
            ],
            'EntityResultTypeRankingOptions': [
                {
                    'ResultType': 'Answer',
                    'MaxEntitySetCount': 6,
                },
            ],
            'MultiEntityMerge': [
                {
                    'EntityTypes': [
                        'File',
                        'External',
                    ],
                    'Size': 15,
                    'From': 0,
                },
            ],
            'SupportedRankingVersion': 1,
        },
    }

    response = requests.post(
        'https://substrate.office.com/searchservice/api/v2/query',
        params=params,
        cookies=cookies,
        headers=headers,
        json=json_data,
    )
    data = response.json()
    result = []
    for entity in data['EntitySets'][0]['ResultSets'][0]['Results']:
        result.append({
            "Title": entity['Source']['Title'],
            "Path": entity['Source']['Path'],
            "LastModifiedTime": entity['Source']['LastModifiedTime'],
            "Summary": entity['Source']['HitHighlightedSummary'],
            "CreatedBy": entity['Source']['AuthorOWSUSER'].split('|')[0],
            "FileType": entity['Source'].get('FileExtension')

        })
    return result


if __name__ == '__main__':
    # simple demo
    results = search_sharepoint('tli')
    for r in results:
        print(r)
