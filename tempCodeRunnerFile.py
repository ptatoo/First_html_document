for lecDisRow in lecDisRows:
                #     lec_dis = {}
                #     lec_dis["classId"] = class_id
                #     lec_dis["lec_dis"] = lecDisRow.find_element(By.CSS_SELECTOR, '[class="sectionColumn"]').text
                #     texts = parseStatus(lecDisRow.find_element(By.CSS_SELECTOR, '[class="statusColumn"]').text)
                #     lec_dis["status"] = texts[0]
                #     lec_dis["total_spots"] = texts[1]
                #     lec_dis["enrolled_spots"] = texts[2]
                #     lec_dis["waitlist_status"] = lecDisRow.find_element(By.CSS_SELECTOR, '[class="waitlistColumn"]').text
                #     lec_dis["days"] = lecDisRow.find_element(By.CSS_SELECTOR, '[class="dayColumn hide-small beforeCollapseHide"]').get_attribute("innerText").strip()
                #     timing = lecDisRow.find_element(By.CSS_SELECTOR, '[class="timeColumn"]').text.split("\n")
                #     texts = parseTime(timing[-1])
                #     lec_dis["start_time"] = texts[0]
                #     lec_dis["end_time"] = texts[1]
                #     lec_dis["location"] = parseLocation(lecDisRow.find_element(By.CSS_SELECTOR, '[class="locationColumn hide-small"]').text)
                #     lec_dis["units"] = lecDisRow.find_element(By.CSS_SELECTOR, '[class="unitsColumn"]').text
                #     lec_dis["instructors"] = lecDisRow.find_element(By.CSS_SELECTOR, '[class="instructorColumn hide-small"]').text
                #     lec_writer.writerow(lec_dis)