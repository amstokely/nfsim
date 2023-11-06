%include "std_string.i"
%include "std_vector.i"
%include "std_map.i"
%include "std_list.i"

%template(StringVector) std::vector<std::string>;
%template(IntVector) std::vector<int>;
%template(StringStringMap) std::map<std::string, std::string>;
%template(VectorStringVector) std::vector<std::vector<std::string> >;
%template(StringList) std::list<std::string>;
