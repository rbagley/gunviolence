
def get_race(i):
  if i['white']=='':
    print(i)
  if i['white'] not in ['NA','error',''] and float(i['white'])>=0:
    races = {
      'white':float(i['white']),
      'black':float(i['black']),
      'latinx':float(i['latinx'])
    }
    #if printed<10: print(races)
    max_group=max(races,key=races.get)
    max_val=float(races[max_group])
    return max_group if max_val>60 else 'other',max_group if max_val>50 else 'other',max_group
    results={
      'supermajority': max_group if max_val>60 else 'other',
      'majority': max_group if max_val>50 else 'other',
      'plurality': max_group
    }
    #if max_group!='white': print(max_group)
    #if printed<10: print(races,max_group)
    return results
  else:
    return 'NA','NA','NA'
    return {
      'supermajority': 'NA',
      'majority': 'NA',
      'plurality': 'NA'
    }