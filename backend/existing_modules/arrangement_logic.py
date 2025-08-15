import pandas as pd
from datetime import date
import traceback
import re
from utils import get_ist_today
from datetime import date, timedelta

class ArrangementLogic:
    """
    Railway-optimized arrangement logic for teacher replacement system.
    Enhanced with comprehensive subject mapping, intelligent category-based matching,
    and robust workload balancing.
    """

    # ... (Poora SUBJECT_MAPPING_CONFIG, STREAMS, CLASS_LEVELS waise ka waisa hi rahega) ...
    # ... (Ismein koi badlaav nahi hai, isliye yahan dobara paste nahi kar raha) ...
    SUBJECT_MAPPING_CONFIG = {
        "MATHEMATICS": ["MATH", "MATHS", "MATHEMATICS", "APPLIED MATH", "APPLIED MATHEMATICS"],
        "SCIENCE": ["SCIENCE", "SCI", "PHYSICS", "CHEMISTRY", "BIOLOGY"],
        "PHYSICS": ["PHYSICS", "PHY", "SCIENCE"],
        "CHEMISTRY": ["CHEMISTRY", "CHEM", "SCIENCE"],
        "BIOLOGY": ["BIOLOGY", "BIO", "SCIENCE"],
        "SST": ["SST", "S.ST", "SOCIAL STUDIES", "SOCIAL SCIENCE", "HISTORY", "GEOGRAPHY", "POLITICAL SCIENCE", "ECONOMICS", "CIVICS"],
        "HISTORY": ["HISTORY", "HIST", "SST", "SOCIAL STUDIES"],
        "GEOGRAPHY": ["GEOGRAPHY", "GEO", "SST", "SOCIAL STUDIES"],
        "POLITICAL SCIENCE": ["POLITICAL SCIENCE", "POL.SC", "CIVICS", "SST"],
        "ECONOMICS": ["ECONOMICS", "ECO", "SST",],
        "CIVICS": ["CIVICS", "POLITICAL SCIENCE", "SST"],
        "COMPUTER SCIENCE": ["COMPUTER SCIENCE", "CS", "COMPUTER", "COMPUTERS", "IT", "ICT", "AI", "ARTIFICIAL INTELLIGENCE"],
        "IT": ["IT", "INFORMATION TECHNOLOGY", "COMPUTER", "CS"],
        "AI": ["AI", "A.I.", "ARTIFICIAL INTELLIGENCE", "COMPUTER", "IT"], 
        "HINDI": ["HINDI", "SANSKRIT"],
        "EVS": ["EVS", "ENVIRONMENTAL SCIENCE", "ENVIRONMENTAL STUDIES"],
        "SANSKRIT": ["SANSKRIT", "SKT", "HINDI"],
        "ENGLISH": ["ENGLISH", "ENG"],
        "BUSINESS STUDIES": ["BUSINESS STUDIES", "BST", "BUSINESS",],
        "BST": ["BST", "BUSINESS STUDIES", "BUSINESS",],
        "ACCOUNTANCY": ["ACCOUNTANCY", "ACCOUNTS", "ACCOUNTING"],
        "ACCOUNTS": ["ACCOUNTS", "ACCOUNTANCY", "ACCOUNTING"],
        "PHYSICAL EDUCATION": ["PE", "PHYSICAL", "PHE", "GAME", "SPORTS"],
        "ART": ["ART", "ARTS", "DRAWING", "PAINTING"],
        "MUSIC": ["MUSIC", "SINGING", "VOCAL"],
        "GK": ["GK", "GENERAL KNOWLEDGE"],
        "MORAL SCIENCE": ["MORAL SCIENCE", "MORAL ED", "VALUE EDUCATION", "VALUES"],
        "URDU": ["URDU"],
        "SOCIOLOGY": ["SOCIOLOGY"],
        "PSYCHOLOGY": ["PSYCHOLOGY"]
    }

    STREAMS = {
        "SCIENCE": ["PHYSICS", "CHEMISTRY", "BIOLOGY", "ENGLISH",],
        "COMMERCE": ["BUSINESS STUDIES", "BST", "ACCOUNTANCY", "ACCOUNTS", "ECONOMICS", "ENGLISH"],
        "ARTS": ["HISTORY", "GEOGRAPHY", "POLITICAL SCIENCE", "ECONOMICS", "ENGLISH",],
        "HUMANITIES": ["HISTORY", "GEOGRAPHY", "POLITICAL SCIENCE", "ECONOMICS", "ENGLISH"],
        "SOCIOLOGY": ["SOCIOLOGY"], 
        "PSYCHOLOGY": ["PSYCHOLOGY"]
    }

    CLASS_LEVELS = {
        "PRIMARY": ["I", "II", "III", "IV", "V","VI" "1", "2", "3", "4", "5","6"],
        "MIDDLE": ["VI", "VII", "VIII", "6", "7", "8"],
        "SECONDARY": ["IX", "X", "9", "10"],
        "SENIOR_SECONDARY": ["XI", "XII", "11", "12"]
    }


    def __init__(self, data_manager_instance):
        """Initialize with DataManager instance for database operations"""
        self.data_manager = data_manager_instance
        all_variations = []
        for variations in self.SUBJECT_MAPPING_CONFIG.values():
            all_variations.extend(variations)
        self.sorted_subject_variations = sorted(list(set(all_variations)), key=len, reverse=True)
        print("--- ArrangementLogic Initialized (Workload Optimized) ---")

    # ... (_get_standardized_subject, _extract_subject_from_class_info, _extract_class_level, _get_stream_for_subject, _can_teach functions waise hi rahenge) ...
    # ... (Inmein koi badlaav nahi hai) ...
    def _get_standardized_subject(self, subject_str):
     """Standardize subject using comprehensive mapping"""
     if not subject_str or not isinstance(subject_str, str):
        return None
    
     s_upper = subject_str.upper().strip()
    
    # Check variations to find the standard key
     for std_subject, variations in self.SUBJECT_MAPPING_CONFIG.items():
        # Ensure variations are also checked in uppercase
        if s_upper in [v.upper() for v in variations]:
            return std_subject
    
    # If no mapping found, return the original subject in uppercase
     return s_upper
    def _extract_subject_from_class_info(self, class_info_str):
        """
        ✅✅✅ FINAL FIX: Finds the subject by searching for known variations in the string.
        This is the most reliable method.
        """
        if not class_info_str or not isinstance(class_info_str, str):
            return None
        
        class_info_upper = class_info_str.upper().strip()
        
        # self.sorted_subject_variations is created in __init__
        # It's sorted by length, so "POLITICAL SCIENCE" is checked before "SCIENCE"
        for variation in self.sorted_subject_variations:
            # Use word boundaries (\b) to ensure we match whole words.
            # This prevents 'ART' from matching inside 'QUARTERLY'.
            # We must escape special characters like '.' in 'A.I.' for regex to work.
            pattern = r'\b' + re.escape(variation.upper()) + r'\b'
            
            # For variations with dots like A.I., the \b might fail. Add an alternative check.
            is_found = False
            if re.search(pattern, class_info_upper):
                is_found = True
            elif variation.find('.') != -1: # If variation has dots (e.g., A.I.)
                # Also check without word boundaries, but surrounded by spaces or at ends
                pattern_no_boundary = r'(^|\s)' + re.escape(variation.upper()) + r'(\s|$)'
                if re.search(pattern_no_boundary, class_info_upper):
                    is_found = True

            if is_found:
                # If a known variation is found, return its standardized form.
                # For example, if 'BST' is found, this returns 'BUSINESS STUDIES'.
                return self._get_standardized_subject(variation)
        
        # If no known subject is found after checking all variations, return None.
        print(f"WARN: Could not extract a known subject from '{class_info_str}'")
        return None


    def _extract_class_level(self, class_info_str):
        """✅ FIXED: Extract class level from class info (Regex now includes 'X')"""
        if not class_info_str or not isinstance(class_info_str, str):
            return None
        
        class_upper = class_info_str.upper().strip()
        
        # ✅ FIXED REGEX
        match = re.search(r'\b(XI|XII|X|IX|IV|V?I{0,3}|[1-9]|1[0-2])\b', class_upper)
        if not match:
            return None
        
        class_val = match.group(1)
        
        # Find level
        for level, classes in self.CLASS_LEVELS.items():
            if class_val in classes:
                return level
        
        return None

    def _get_stream_for_subject(self, subject):
        """Get stream for a subject"""
        if not subject:
            return None
        
        std_subject = self._get_standardized_subject(subject)
        
        for stream, subjects in self.STREAMS.items():
            std_stream_subjects = [self._get_standardized_subject(s) for s in subjects]
            if std_subject in std_stream_subjects:
                return stream
        
        return None

    def _can_teach(self, candidate_subjects_str, target_subjects_list):
     """
     Checks if a candidate can teach ANY of the subjects from the target list.
     target_subjects_list: Can be a single subject string or a list of subject strings.
     """
    # If there's no specific subject requirement, any teacher can "teach" it.
     if not target_subjects_list:
        return True
    
    # If the candidate has no subjects listed, they can't teach anything specific.
     if not candidate_subjects_str or not isinstance(candidate_subjects_str, str):
        return False

    # Ensure target_subjects is always a list for consistent processing
     if isinstance(target_subjects_list, str):
        target_subjects_list = [target_subjects_list]

    # Standardize all target subjects from the input list
     std_target_subjects = {self._get_standardized_subject(s) for s in target_subjects_list if s}
     if not std_target_subjects: # If list was empty or contained only invalid subjects
        return True 

    # Get all subjects the candidate teaches
     candidate_subjects_list = [s.strip() for s in candidate_subjects_str.split(',') if s.strip()]
     if not candidate_subjects_list:
        return False
    
    # Standardize all candidate subjects
     std_candidate_subjects = {self._get_standardized_subject(s) for s in candidate_subjects_list if s}

    # The core logic: Check if there is any intersection between the two sets of subjects.
    # This is the most efficient way to see if ANY candidate subject matches ANY target subject.
     if not std_candidate_subjects.isdisjoint(std_target_subjects):
        return True

    # Additionally, check for broader mappings (e.g., candidate teaches PHYSICS, target is SCIENCE)
     for cand_subj in std_candidate_subjects:
        for target_subj in std_target_subjects:
            # Check if candidate's subject is a variation of the target subject
            if cand_subj in [v.upper() for v in self.SUBJECT_MAPPING_CONFIG.get(target_subj, [])]:
                return True
            # Check if target's subject is a variation of the candidate's subject
            if target_subj in [v.upper() for v in self.SUBJECT_MAPPING_CONFIG.get(cand_subj, [])]:
                return True

     return False

    # ⭐️⭐️⭐️ ASLI BADLAAV IS FUNCTION MEIN HAI ⭐️⭐️⭐️
    def _find_candidates(self, candidates_df, search_criteria, daily_workload_map, historical_workload_map):
        """
        Finds the best candidate with two-level workload balancing.
        1. Filters candidates by category/subject.
        2. Sorts the qualified pool by:
           - First by DAILY workload (less is better).
           - Then by HISTORICAL workload (less is better) as a tie-breaker.
        """
        if candidates_df.empty:
            return None

        # Step 1 & 2: Filter by Category and Subject (No change here)
        filtered_candidates = candidates_df.copy()
        category_to_find = search_criteria.get('category')
        if category_to_find:
            filtered_candidates = filtered_candidates[
                filtered_candidates['category'].astype(str).str.replace('.', '', regex=False).str.strip().str.upper() == category_to_find.upper()
            ]
        if filtered_candidates.empty: return None

        subjects_to_match = search_criteria.get('subject')
        if subjects_to_match:
            qualified_indices = [idx for idx, row in filtered_candidates.iterrows() if self._can_teach(row.get('subject', ''), subjects_to_match)]
            if not qualified_indices: return None
            filtered_candidates = filtered_candidates.loc[qualified_indices]
        if filtered_candidates.empty: return None

        # Step 3: Filter by Teaching Class (No change here)
        candidate_class_req = search_criteria.get('candidate_teaches_class')
        if candidate_class_req:
            class_columns = [f'period{i}' for i in range(1, 8)]
            qualified_indices_by_class = [
                idx for idx, row in filtered_candidates.iterrows()
                if any(match.group(1) in candidate_class_req for col in class_columns if (match := re.search(r'\b(XI|XII|X|IX|IV|V?I{0,3}|[1-9]|1[0-2])\b', str(row.get(col, '')).upper())))
            ]
            if not qualified_indices_by_class: return None
            filtered_candidates = filtered_candidates.loc[qualified_indices_by_class]
        if filtered_candidates.empty: return None

        # ⭐️⭐️⭐️ YAHAN HAI ASLI WORKLOAD LOGIC ⭐️⭐️⭐️
        # Step 4: Add BOTH workload columns to the filtered candidates
        filtered_candidates['daily_workload'] = filtered_candidates['teacher_id'].astype(str).str.upper().map(daily_workload_map).fillna(0).astype(int)
        filtered_candidates['historical_workload'] = filtered_candidates['teacher_id'].astype(str).str.upper().map(historical_workload_map).fillna(0).astype(int)

        # Step 5: Sort by Daily workload first, then Historical workload
        sorted_candidates = filtered_candidates.sort_values(
            by=['daily_workload', 'historical_workload', 'name'],
            ascending=[True, True, True]
        )

        print(f"DEBUG: Found {len(sorted_candidates)} qualified candidates. Picking best by workload.")
        # print(sorted_candidates[['name', 'daily_workload', 'historical_workload']].to_string()) # Uncomment for deep debugging

        # Step 6: Return the best candidate (sabse upar wala)
        return sorted_candidates.iloc[0].to_dict()



# arrangement_logic.py ke andar is naye function ko paste karein

    def find_replacement_teacher(self, school_id, absent_teacher_id, period, schedules_df, all_absent_today, assigned_in_this_period):
        """
        Advanced replacement logic v4. Uses a dynamically updated list of teachers busy in the current period.
        """
        print(f"\n--- ADVANCED REPLACEMENT LOGIC v4: School={school_id}, Absent={absent_teacher_id}, Period={period} ---")
        try:
            absent_row = schedules_df[schedules_df['teacher_id'].astype(str).str.upper() == str(absent_teacher_id).upper()]
            if absent_row.empty:
                user_detail = self.data_manager.get_user_details_by_teacher_id(school_id, absent_teacher_id)
                absent_name = user_detail.get("name", "Unknown") if user_detail else "Unknown"
                return None, None, None, absent_name, "Teacher Not in Schedule"

            absent_details = absent_row.iloc[0]
            absent_name = str(absent_details.get('name', 'Unknown'))
            period_col = f'period{period}'
            
            # --- ✅ FINAL EXCLUSION LOGIC ---
            # Final exclusion list = Aaj ke sabhi absent teachers + jo is period mein pehle se busy hain
            exclusion_list = list(set(all_absent_today + assigned_in_this_period))
            exclusion_list_upper = [str(tid).upper() for tid in exclusion_list if tid]

            free_teachers_df = schedules_df[
                (schedules_df[period_col].fillna('FREE').astype(str).str.upper() == 'FREE') &
                (~schedules_df['teacher_id'].astype(str).str.upper().isin(exclusion_list_upper))
            ].copy()

            if free_teachers_df.empty:
                print(f"INFO: No free and un-assigned teachers available for Period {period}.")
                return None, None, None, absent_name, "No Free Teachers"

            # --- Baaki ka logic (workload, search pipeline) ab is 'free_teachers_df' par chalega ---
            period_cols = [f'period{i}' for i in range(1, 8)]
            daily_workload_map = {str(row['teacher_id']).upper(): sum(1 for col in period_cols if str(row.get(col, '')).strip().upper() not in ['FREE', 'NAN', '']) for _, row in schedules_df.iterrows()}
            candidate_ids = free_teachers_df['teacher_id'].astype(str).tolist()
            historical_workloads_data = self.data_manager.get_multiple_teachers_workload(school_id, candidate_ids)
            historical_workload_map = {str(item["teacher_id"]).upper(): item.get("workload_count", 0) for item in historical_workloads_data}
            
            # --- Aapka poora, detailed search pipeline (bilkul a_sahi hai) ---
            raw_category = str(absent_details.get('category', ''))
            absent_category = raw_category.replace('.', '',).strip().upper()
            class_info = absent_details.get(period_col, 'FREE')
            search_subject = self._extract_subject_from_class_info(class_info)
            class_level = self._extract_class_level(class_info)
            class_val_match = re.search(r'\b(XI|XII|X|IX|IV|V?I{0,3}|[1-9]|1[0-2])\b', class_info.upper())
            class_val = class_val_match.group(1) if class_val_match else None
            search_pipeline = []
            custom_rules = self.data_manager.get_arrangement_rules(school_id)

            search_pipeline = []

            # 2. Agar custom rules mile, to unka istemal karo
            if custom_rules:
                print(f"INFO: Found {len(custom_rules)} custom rules for {school_id}. Using DATABASE LOGIC.")
                
                absent_category = str(absent_details.get('category', '')).replace('.', '').strip().upper()
                class_info = absent_details.get(period_col, 'FREE')
                search_subject = self._extract_subject_from_class_info(class_info)

                for rule in custom_rules:
                    criteria = rule.get('criteria', {})
                    if absent_category in criteria.get('absent_category', []):
                        search_criteria = {'quality': rule['rule_name']}
                        search_criteria['category'] = criteria.get('candidate_category')
                        if criteria.get('subject_match') == 'exact':
                            search_criteria['subject'] = search_subject
                        else:
                            search_criteria['subject'] = None
                        search_pipeline.append(search_criteria)
            
            # 3. Agar koi custom rule nahi mila, to apne default logic ka istemal karo
            else:
                print(f"INFO: No custom rules for {school_id}. Using DEFAULT BUILT-IN LOGIC.")
                
                # --- YAHAN AAPKA POORA PURANA, POWERFUL LOGIC AAYEGA ---
                raw_category = str(absent_details.get('category', ''))
                absent_category = raw_category.replace('.', '').strip().upper()
                class_info = absent_details.get(period_col, 'FREE')
                search_subject = self._extract_subject_from_class_info(class_info)
                class_level = self._extract_class_level(class_info)
                class_val_match = re.search(r'\b(XI|XII|X|IX|IV|V?I{0,3}|[1-9]|1[0-2])\b', class_info.upper())
                class_val = class_val_match.group(1) if class_val_match else None
                
            # ... (Poora TGT, PGT, PRT ka search_pipeline waise hi rahega) ...
            if absent_category == 'PRT':
                search_pipeline = [
                    {'quality': 'Ideal - Same Category, Same Subject', 'category': 'PRT', 'subject': search_subject}
                ]
                if class_level == 'PRIMARY':
                    search_pipeline.append(
                        {'quality': 'Good - TGT (Class 6-8) for Adjacent Class', 'category': 'TGT', 'subject': search_subject, 'condition': class_val in ['V','VI','5','6'], 'candidate_teaches_class': ['VI', 'VII', 'VIII', '6', '7', '8']}
                    )
                elif class_level == 'MIDDLE':
                    search_pipeline.append(
                        {'quality': 'Good - TGT with Same Subject for Middle Class', 'category': 'TGT', 'subject': search_subject}
                    )
                search_pipeline.append(
                    {'quality': 'Acceptable - Same Category, Any Subject', 'category': 'PRT', 'subject': None}
                )

# --- TGT LOGIC (FINAL VERSION - YOUR LOGIC + MY FIX) ---
            elif absent_category == 'TGT':
                search_pipeline = []
                std_subject = self._get_standardized_subject(search_subject)

                # --- Condition 1: Agar absent teacher 9th ya 10th class mein hai ---
                if class_val in ['IX', 'X', '9', '10']:
                    print("INFO: Applying ADVANCED rules for Secondary Classes (IX, X)")
                    
                    # Priority 1: Sabse pehle, TGT dhoondho jo 9-10 padhata ho aur subject bhi same ho.
                    search_pipeline.append({
                        'quality': 'Ideal - TGT (Teaches 9-10), Same Subject', 
                        'category': 'TGT', 
                        'subject': search_subject,
                        'candidate_teaches_class': ['IX', 'X', '9', '10'] # YEH FIX ZAROORI HAI
                    })
                    
                    # Priority 1.5: Aapka specific subject logic (Hindi/CS)
                    if std_subject == 'HINDI':
                        search_pipeline.append({
                            'quality': 'Good - TGT (Teaches 9-10), Related (Sanskrit)', 
                            'category': 'TGT', 
                            'subject': 'SANSKRIT',
                            'candidate_teaches_class': ['IX', 'X', '9', '10'] # Yahan bhi filter zaroori hai
                        })
                    elif std_subject == 'COMPUTER SCIENCE':
                        search_pipeline.append({
                            'quality': 'Good - TGT (Teaches 9-10), Related (IT/AI)', 
                            'category': 'TGT', 
                            'subject': ['IT', 'AI'],
                            'candidate_teaches_class': ['IX', 'X', '9', '10'] # Yahan bhi filter zaroori hai
                        })

                    # Priority 2: PGT dhoondho jiska subject same ho.
                    search_pipeline.append({
                        'quality': 'Very Good - PGT, Same Subject', 
                        'category': 'PGT', 
                        'subject': search_subject
                    })
                    
                    # Priority 2.5: Aapka PGT related subject logic
                    related_subjects_pgt = []
                    if std_subject in ['SCIENCE', 'PHYSICS', 'CHEMISTRY', 'BIOLOGY']:
                        related_subjects_pgt = [s for s in ['PHYSICS', 'CHEMISTRY', 'BIOLOGY'] if s != std_subject]
                    elif std_subject in ['SST', 'HISTORY', 'GEOGRAPHY', 'POLITICAL SCIENCE', 'ECONOMICS', 'CIVICS']:
                        related_subjects_pgt = [s for s in ['HISTORY', 'GEOGRAPHY', 'POLITICAL SCIENCE', 'ECONOMICS', 'CIVICS'] if s != std_subject]
                    
                    if related_subjects_pgt:
                        search_pipeline.append({
                            'quality': 'Acceptable - PGT, Related Subject', 
                            'category': 'PGT', 
                            'subject': related_subjects_pgt
                        })

                    # Priority 3: Koi bhi TGT dhoondho jo 9-10 padhata ho (subject koi bhi ho).
                    search_pipeline.append({
                        'quality': 'Suboptimal - TGT (Teaches 9-10), Any Subject', 
                        'category': 'TGT', 
                        'subject': None,
                        'candidate_teaches_class': ['IX', 'X', '9', '10'] # YEH FIX ZAROORI HAI
                    })
                    
                    # Priority 4 (Last Resort): Koi bhi PGT laga do.
                    search_pipeline.append({
                        'quality': 'Fallback - Any PGT', 
                        'category': 'PGT', 
                        'subject': None
                    })

                # --- Condition 2: Agar absent teacher 6th, 7th, ya 8th class mein hai ---
                # (Aapka original logic bilkul sahi tha iske liye)
                elif class_val in ['VI', 'VII', 'VIII', '6', '7', '8']:
                    print("INFO: Applying rules for Middle Classes (VI, VII, VIII)")
                    search_pipeline.extend([
                        {'quality': 'Ideal - TGT, Same Subject', 'category': 'TGT', 'subject': search_subject},
                        {'quality': 'Good - PGT, Same Subject', 'category': 'PGT', 'subject': search_subject},
                        {'quality': 'Acceptable - Any TGT', 'category': 'TGT', 'subject': None},
                        {'quality': 'Fallback - Any PGT', 'category': 'PGT', 'subject': None}
                    ])

                # --- Condition 3: Agar TGT teacher Primary section mein padha raha hai ---
                # (Aapka original logic bilkul sahi tha iske liye)
                elif class_val in ['IV', 'V', '4', '5']:
                     print("INFO: Applying rules for TGT in Primary Classes (IV, V)")
                     search_pipeline.extend([
                        {'quality': 'Ideal - TGT, Same Subject', 'category': 'TGT', 'subject': search_subject},
                        {'quality': 'Good - PRT, Same Subject', 'category': 'PRT', 'subject': search_subject},
                        {'quality': 'Acceptable - Any TGT', 'category': 'TGT', 'subject': None},
                        {'quality': 'Fallback - Any PRT', 'category': 'PRT', 'subject': None}
                    ])
                
                # --- Default Fallback (Agar class inmein se koi nahi hai) ---
                else:
                    print("INFO: Applying default fallback rules for TGT.")
                    search_pipeline.append(
                        {'quality': 'Fallback - Any TGT', 'category': 'TGT', 'subject': None}
                    )
            elif absent_category == 'PGT':
                search_pipeline = []
                std_subject = self._get_standardized_subject(search_subject)

                # Step 1: Ideal Match - Hamesha sabse pehle
                search_pipeline.append(
                    {'quality': 'Ideal - PGT with Same Subject', 'category': 'PGT', 'subject': search_subject}
                )

                # Step 2: Very Good Match - TGT for Same Subject (Aapki PGT -> TGT wali problem solve karega)
                # Yeh niyam ab har PGT ke liye check hoga.
                search_pipeline.append(
                    {'quality': 'Very Good - TGT with Same Subject', 'category': 'TGT', 'subject': search_subject}
                )

                # Step 3: Detailed Rules based on Class Level and Stream
                if class_level == 'SENIOR_SECONDARY': # Classes 11, 12
                    stream = self._get_stream_for_subject(search_subject)
                    # Stream-based logic
                    if stream == 'COMMERCE':
                        search_pipeline.append({'quality': 'Good - PGT from Same Stream (Commerce)', 'category': 'PGT', 'subject': self.STREAMS.get("COMMERCE", [])})
                    elif stream == 'SCIENCE':
                        search_pipeline.append({'quality': 'Good - PGT from Same Stream (Science)', 'category': 'PGT', 'subject': self.STREAMS.get("SCIENCE", [])})
                    elif stream in ['ARTS', 'HUMANITIES']:
                         search_pipeline.append({'quality': 'Good - PGT from Same Stream (Arts)', 'category': 'PGT', 'subject': self.STREAMS.get("ARTS", [])})
                    
                    # Subject-specific cross-category logic
                    if std_subject == 'ENGLISH':
                        search_pipeline.append({'quality': 'Acceptable - TGT (9/10) for English', 'category': 'TGT', 'subject': 'ENGLISH', 'candidate_teaches_class': ['IX', 'X', '9', '10']})
                    elif std_subject == 'COMPUTER SCIENCE':
                        search_pipeline.append({'quality': 'Acceptable - TGT (9/10) for CS/IT/AI', 'category': 'TGT', 'subject': ['COMPUTER SCIENCE', 'IT', 'AI'], 'candidate_teaches_class': ['IX', 'X', '9', '10']})

                elif class_level == 'SECONDARY': # Classes 9, 10
                    # Related subjects logic for PGTs
                    related_subjects_pgt = []
                    if std_subject in ['SCIENCE', 'PHYSICS', 'CHEMISTRY', 'BIOLOGY']:
                        related_subjects_pgt = [s for s in ['PHYSICS', 'CHEMISTRY', 'BIOLOGY'] if s != std_subject]
                    elif std_subject in ['SST', 'HISTORY', 'GEOGRAPHY', 'POLITICAL SCIENCE', 'ECONOMICS', 'CIVICS']:
                        related_subjects_pgt = [s for s in ['HISTORY', 'GEOGRAPHY', 'POLITICAL SCIENCE', 'ECONOMICS', 'CIVICS'] if s != std_subject]
                    elif std_subject == 'MATHEMATICS':
                        related_subjects_pgt = ['APPLIED MATHEMATICS']
                    
                    if related_subjects_pgt:
                        search_pipeline.append({'quality': 'Acceptable - PGT with Related Subject', 'category': 'PGT', 'subject': related_subjects_pgt})
                    
                    # Related subjects for TGTs
                    if std_subject == 'HINDI':
                        search_pipeline.append({'quality': 'Acceptable - TGT with Sanskrit', 'category': 'TGT', 'subject': 'SANSKRIT'})
                
                # Step 4: UNIVERSAL FALLBACK - YEH AB HAMESHA CHALEGA
                # Yeh niyam ab sabse aakhir mein, bina kisi if/else ke, add hoga.
                # Isse "UNASSIGNED" wali problem 100% khatm ho jayegi.
                search_pipeline.append(
                    {'quality': 'Fallback - Any free PGT teacher', 'category': 'PGT', 'subject': None}
                )

            # --- SEARCH EXECUTION LOOP (Ismein koi badlaav nahi) ---
            for criteria in search_pipeline:
                if 'condition' in criteria and not criteria['condition']:
                    continue
                
                print(f"DEBUG: Searching with criteria: {criteria['quality']}")
                
                best_candidate_dict = self._find_candidates(free_teachers_df, criteria, daily_workload_map, historical_workload_map)
                if best_candidate_dict:
                    replacement_id = str(best_candidate_dict.get("teacher_id", "")).strip()
                    replacement_category = str(best_candidate_dict.get("category", "")).replace('.', '').strip().upper()
                    replacement_name = str(best_candidate_dict.get("name", "")).strip()
                    quality = criteria['quality']
                    
                    self.data_manager.update_teacher_workload(school_id, replacement_id)
                    return replacement_id, replacement_category, replacement_name, absent_name, quality
            
            # Agar poori pipeline ke baad bhi koi nahi mila (ab iske chances bohot kam hain)
            return None, None, None, absent_name, "No Suitable Replacement"
        except Exception as e:
            print(f"CRITICAL ERROR in find_replacement_teacher: {e}")
            traceback.print_exc()
            return None, None, None, "Unknown", "Error Occurred"