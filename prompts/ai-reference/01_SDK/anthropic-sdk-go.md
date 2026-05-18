---

Anthropic Go API 라이브러리

Anthropic Go 라이브러리는 Go로 작성된 애플리케이션에서 Anthropic REST API에
편리하게 접근할 수 있도록 한다.
설치

import (
	"github.com/anthropics/anthropic-sdk-go" // imported as anthropic
)

버전을 고정하려면:

go get -u 'github.com/anthropics/anthropic-sdk-go@v1.26.0'

요구사항
이 라이브러리는 Go 1.22+ 가 필요하다.
사용법
이 라이브러리의 전체 API는 api.md 에서 확인할 수 있다.
package main

import (
	"context"
	"fmt"

	"github.com/anthropics/anthropic-sdk-go"
	"github.com/anthropics/anthropic-sdk-go/option"
)

func main() {
	client := anthropic.NewClient(
		option.WithAPIKey("my-anthropic-api-key"), // defaults to os.LookupEnv("ANTHROPIC_API_KEY")
	)
	message, err := client.Messages.New(context.TODO(), anthropic.MessageNewParams{
		MaxTokens: 1024,
		Messages: []anthropic.MessageParam{
			anthropic.NewUserMessage(anthropic.NewTextBlock("What is a quaternion?")),
		},
		Model: anthropic.ModelClaudeSonnet4_5_20250929,
	})
	if err != nil {
		panic(err.Error())
	}
	fmt.Printf("%+v\n", message.Content)
}

대화(Conversations)
messages := []anthropic.MessageParam{
    anthropic.NewUserMessage(anthropic.NewTextBlock("What is my first name?")),
}

message, err := client.Messages.New(context.TODO(), anthropic.MessageNewParams{
    Model:     anthropic.ModelClaudeSonnet4_5_20250929,
    Messages:  messages,
    MaxTokens: 1024,
})
if err != nil {
    panic(err)
}

fmt.Printf("%+v\n", message.Content)

messages = append(messages, message.ToParam())
messages = append(messages, anthropic.NewUserMessage(
    anthropic.NewTextBlock("My full name is John Doe"),
))

message, err = client.Messages.New(context.TODO(), anthropic.MessageNewParams{
    Model:     anthropic.ModelClaudeSonnet4_5_20250929,
    Messages:  messages,
    MaxTokens: 1024,
})

fmt.Printf("%+v\n", message.Content)

System prompt
message, err := client.Messages.New(context.TODO(), anthropic.MessageNewParams{
    Model:     anthropic.ModelClaudeSonnet4_5_20250929,
    MaxTokens: 1024,
    System: []anthropic.TextBlockParam{
        {Text: "Be very serious at all times."},
    },
    Messages: messages,
})

Streaming
content := "What is a quaternion?"

stream := client.Messages.NewStreaming(context.TODO(), anthropic.MessageNewParams{
    Model:     anthropic.ModelClaudeSonnet4_5_20250929,
    MaxTokens: 1024,
    Messages: []anthropic.MessageParam{
        anthropic.NewUserMessage(anthropic.NewTextBlock(content)),
    },
})

message := anthropic.Message{}
for stream.Next() {
    event := stream.Current()
    err := message.Accumulate(event)
    if err != nil {
        panic(err)
    }

    switch eventVariant := event.AsAny().(type) {
        case anthropic.ContentBlockDeltaEvent:
        switch deltaVariant := eventVariant.Delta.AsAny().(type) {
        case anthropic.TextDelta:
            print(deltaVariant.Text)
        }

    }
}

if stream.Err() != nil {
    panic(stream.Err())
}

Tool calling
package main

import (
	"context"
	"encoding/json"
	"fmt"

	"github.com/anthropics/anthropic-sdk-go"
	"github.com/invopop/jsonschema"
)

func main() {
	client := anthropic.NewClient()

	content := "Where is San Francisco?"

	println("[user]: " + content)

	messages := []anthropic.MessageParam{
		anthropic.NewUserMessage(anthropic.NewTextBlock(content)),
	}

	toolParams := []anthropic.ToolParam{
		{
			Name:        "get_coordinates",
			Description: anthropic.String("Accepts a place as an address, then returns the latitude and longitude coordinates."),
			InputSchema: GetCoordinatesInputSchema,
		},
	}
	tools := make([]anthropic.ToolUnionParam, len(toolParams))
	for i, toolParam := range toolParams {
		tools[i] = anthropic.ToolUnionParam{OfTool: &toolParam}
	}

	for {
		message, err := client.Messages.New(context.TODO(), anthropic.MessageNewParams{
			Model:     anthropic.ModelClaudeSonnet4_5_20250929,
			MaxTokens: 1024,
			Messages:  messages,
			Tools:     tools,
		})

		if err != nil {
			panic(err)
		}

		print(color("[assistant]: "))
		for _, block := range message.Content {
			switch block := block.AsAny().(type) {
			case anthropic.TextBlock:
				println(block.Text)
				println()
			case anthropic.ToolUseBlock:
				inputJSON, _ := json.Marshal(block.Input)
				println(block.Name + ": " + string(inputJSON))
				println()
			}
		}

		messages = append(messages, message.ToParam())
		toolResults := []anthropic.ContentBlockParamUnion{}

		for _, block := range message.Content {
			switch variant := block.AsAny().(type) {
			case anthropic.ToolUseBlock:
				print(color("[user (" + block.Name + ")]: "))

				var response any
				switch block.Name {
				case "get_coordinates":
					var input struct {
						Location string `json:"location"`
					}

					err := json.Unmarshal([]byte(variant.JSON.Input.Raw()), &input)
					if err != nil {
						panic(err)
					}

					response = GetCoordinates(input.Location)
				}

				b, err := json.Marshal(response)
				if err != nil {
					panic(err)
				}

				println(string(b))

				toolResults = append(toolResults, anthropic.NewToolResultBlock(block.ID, string(b), false))
			}

		}
		if len(toolResults) == 0 {
			break
		}
		messages = append(messages, anthropic.NewUserMessage(toolResults...))
	}
}

type GetCoordinatesInput struct {
	Location string `json:"location" jsonschema_description:"The location to look up."`
}

var GetCoordinatesInputSchema = GenerateSchema[GetCoordinatesInput]()

type GetCoordinateResponse struct {
	Long float64 `json:"long"`
	Lat  float64 `json:"lat"`
}

func GetCoordinates(location string) GetCoordinateResponse {
	return GetCoordinateResponse{
		Long: -122.4194,
		Lat:  37.7749,
	}
}

func GenerateSchema[T any]() anthropic.ToolInputSchemaParam {
	reflector := jsonschema.Reflector{
		AllowAdditionalProperties: false,
		DoNotReference:            true,
	}
	var v T

	schema := reflector.Reflect(v)

	return anthropic.ToolInputSchemaParam{
		Properties: schema.Properties,
	}
}

func color(s string) string {
	return fmt.Sprintf("\033[1;%sm%s\033[0m", "33", s)
}

Tool helper
SDK는 tool을 정의하고 자동 대화 루프를 실행하기 위한 헬퍼 함수를 제공한다. 다음은 기본 예시이다:
package main

import (
	"context"
	"fmt"

	"github.com/anthropics/anthropic-sdk-go"
	"github.com/anthropics/anthropic-sdk-go/toolrunner"
)

// GetWeatherInput defines the tool input with jsonschema tags for automatic schema generation
type GetWeatherInput struct {
	City string `json:"city" jsonschema:"required,description=The city name"`
}

func main() {
	client := anthropic.NewClient()

	// Define a tool - the schema is generated automatically from the struct's jsonschema tags
	weatherTool, err := toolrunner.NewBetaToolFromJSONSchema(
		"get_weather",
		"Get weather for a city",
		func(ctx context.Context, input GetWeatherInput) (anthropic.BetaToolResultBlockParamContentUnion, error) {
			return anthropic.BetaToolResultBlockParamContentUnion{
				OfText: &anthropic.BetaTextBlockParam{
					Text: fmt.Sprintf("The weather in %s is sunny, 72°F", input.City),
				},
			}, nil
		},
	)
	if err != nil {
		panic(err)
	}

	// Create a tool runner that automatically handles the conversation loop
	runner := client.Beta.Messages.NewToolRunner([]anthropic.BetaTool{weatherTool}, anthropic.BetaToolRunnerParams{
		BetaMessageNewParams: anthropic.BetaMessageNewParams{
			Model:     anthropic.ModelClaudeSonnet4_20250514,
			MaxTokens: 1024,
			Messages: []anthropic.BetaMessageParam{
				anthropic.NewBetaUserMessage(anthropic.NewBetaTextBlock("What's the weather in Paris?")),
			},
		},
		MaxIterations: 5,
	})

	// Run until Claude produces a final response
	message, err := runner.RunToCompletion(context.Background())
	if err != nil {
		panic(err)
	}
	fmt.Println(message.Content[0].Text)
}
자세한 내용은 tools.md 를 참고한다.

요청 필드(Request fields)
anthropic 라이브러리는 요청 필드에 대해 Go 1.24+ encoding/json 릴리스의
omitzero 시맨틱을 사용한다.
필수 원시(primitive) 필드(int64, string 등)는 `json:"...,required"` 태그를 가진다. 이
필드들은 zero 값이라도 항상 직렬화된다.
선택적 원시 타입은 param.Opt[T] 로 감싸진다. 이 필드들은 제공된 생성자 anthropic.String(string), anthropic.Int(int64) 등으로 설정할 수 있다.
모든 param.Opt[T], map, slice, struct 또는 string enum은
`json:"...,omitzero"` 태그를 사용한다. zero 값은 생략된 것으로 간주된다.
param.IsOmitted(any) 함수로 omitzero 필드의 존재 여부를 확인할 수 있다.
p := anthropic.ExampleParams{
	ID:   "id_xxx",                // required property
	Name: anthropic.String("..."), // optional property

	Point: anthropic.Point{
		X: 0,                // required field will serialize as 0
		Y: anthropic.Int(1), // optional field will serialize as 1
		// ... omitted non-required fields will not be serialized
	},

	Origin: anthropic.Origin{}, // the zero value of [Origin] is considered omitted
}
param.Opt[T] 대신 null 을 보내려면 param.Null[T]() 을 사용한다.
구조체 T 대신 null 을 보내려면 param.NullStruct[T]() 를 사용한다.
p.Name = param.Null[string]()       // 'null' instead of string
p.Point = param.NullStruct[Point]() // 'null' instead of struct

param.IsNull(p.Name)  // true
param.IsNull(p.Point) // true
요청 구조체는 .SetExtraFields(map[string]any) 메서드를 포함하며, 이를 통해 요청 본문에
스펙에 맞지 않는 필드를 보낼 수 있다. extra field는 일치하는 키를 가진
어떤 struct field 든 덮어쓴다.
경고보안상의 이유로 SetExtraFields 는 신뢰할 수 있는 데이터에 대해서만 사용한다.

구조체 대신 커스텀 값을 보내려면 param.Override[T](value) 를 사용한다.
// In cases where the API specifies a given type,
// but you want to send something else, use [SetExtraFields]:
p.SetExtraFields(map[string]any{
	"x": 0.01, // send "x" as a float instead of int
})

// Send a number instead of an object
custom := param.Override[anthropic.FooParams](12)
요청 union(Request unions)
union은 각 variant에 대해 "Of" 접두사가 붙은 필드를 가진 struct로 표현되며,
오직 하나의 필드만 non-zero 일 수 있다. non-zero 필드가 직렬화된다.
union의 하위 속성은 union struct의 메서드를 통해 접근할 수 있다.
이 메서드들은 존재하는 경우 기저 데이터에 대한 변경 가능한 포인터를 반환한다.
// Only one field can be non-zero, use param.IsOmitted() to check if a field is set
type AnimalUnionParam struct {
	OfCat *Cat `json:",omitzero,inline`
	OfDog *Dog `json:",omitzero,inline`
}

animal := AnimalUnionParam{
	OfCat: &Cat{
		Name: "Whiskers",
		Owner: PersonParam{
			Address: AddressParam{Street: "3333 Coyote Hill Rd", Zip: 0},
		},
	},
}

// Mutating a field
if address := animal.GetOwner().GetAddress(); address != nil {
	address.ZipCode = 94304
}
응답 객체(Response objects)
응답 struct의 모든 필드는 일반 값 타입이다(포인터나 wrapper가 아님).
응답 struct는 또한 각 속성에 대한 메타데이터를 담은 특수한 JSON 필드를 포함한다.
type Animal struct {
	Name   string `json:"name,nullable"`
	Owners int    `json:"owners"`
	Age    int    `json:"age"`
	JSON   struct {
		Name        respjson.Field
		Owner       respjson.Field
		Age         respjson.Field
		ExtraFields map[string]respjson.Field
	} `json:"-"`
}
선택적 데이터를 처리하려면 JSON 필드의 .Valid() 메서드를 사용한다.
.Valid() 는 필드가 null이 아니거나, 존재하지 않거나, marshaling 할 수 없는 경우에 true를 반환한다.
.Valid() 가 false이면 해당 필드는 단순히 zero 값이 된다.
raw := `{"owners": 1, "name": null}`

var res Animal
json.Unmarshal([]byte(raw), &res)

// Accessing regular fields

res.Owners // 1
res.Name   // ""
res.Age    // 0

// Optional field checks

res.JSON.Owners.Valid() // true
res.JSON.Name.Valid()   // false
res.JSON.Age.Valid()    // false

// Raw JSON values

res.JSON.Owners.Raw()                  // "1"
res.JSON.Name.Raw() == "null"          // true
res.JSON.Name.Raw() == respjson.Null   // true
res.JSON.Age.Raw() == ""               // true
res.JSON.Age.Raw() == respjson.Omitted // true
이 .JSON struct는 또한 struct에 명시되지 않은 JSON 응답의 속성을
모두 포함하는 ExtraFields 맵을 포함한다. 이는 아직 SDK에 포함되지 않은
API 기능에 유용하다.
body := res.JSON.ExtraFields["my_unexpected_field"].Raw()
응답 union(Response Unions)
응답에서 union은 각 객체 variant의 모든 가능한 필드를 포함하는
평탄화된(flattened) struct로 표현된다.
variant로 변환하려면 .AsFooVariant() 메서드를 사용하거나, 존재하는 경우 .AsAny() 메서드를 사용한다.
응답 값 union이 원시 값을 포함하는 경우, 원시 필드들은 속성들과 함께 위치하지만
Of 접두사가 붙고 json:"...,inline" 태그를 가진다.
type AnimalUnion struct {
	// From variants [Dog], [Cat]
	Owner Person `json:"owner"`
	// From variant [Dog]
	DogBreed string `json:"dog_breed"`
	// From variant [Cat]
	CatBreed string `json:"cat_breed"`
	// ...

	JSON struct {
		Owner respjson.Field
		// ...
	} `json:"-"`
}

// If animal variant
if animal.Owner.Address.ZipCode == "" {
	panic("missing zip code")
}

// Switch on the variant
switch variant := animal.AsAny().(type) {
case Dog:
case Cat:
default:
	panic("unexpected type")
}
RequestOptions
이 라이브러리는 functional options 패턴을 사용한다. option 패키지에 정의된 함수들은
RequestOption 을 반환하는데, 이는 RequestConfig 를 변경하는 클로저이다. 이러한 옵션은
client 또는 개별 요청에 제공할 수 있다. 예를 들어:
client := anthropic.NewClient(
	// Adds a header to every request made by the client
	option.WithHeader("X-Some-Header", "custom_header_info"),
)

client.Messages.New(context.TODO(), ...,
	// Override the header
	option.WithHeader("X-Some-Header", "some_other_custom_header_info"),
	// Add an undocumented field to the request body, using sjson syntax
	option.WithJSONSet("some.json.path", map[string]string{"my": "object"}),
)
디버깅 시 option.WithDebugLog(nil) 요청 옵션이 유용할 수 있다.
요청 옵션의 전체 목록을 참고한다.
페이지네이션(Pagination)
이 라이브러리는 paginated list endpoint를 다루기 위한 몇 가지 편의 기능을 제공한다.
.ListAutoPaging() 메서드를 사용해 모든 페이지의 항목을 순회할 수 있다:
iter := client.Messages.Batches.ListAutoPaging(context.TODO(), anthropic.MessageBatchListParams{
	Limit: anthropic.Int(20),
})
// Automatically fetches more pages as needed.
for iter.Next() {
	messageBatch := iter.Current()
	fmt.Printf("%+v\n", messageBatch)
}
if err := iter.Err(); err != nil {
	panic(err.Error())
}
또는 단순한 .List() 메서드를 사용해 단일 페이지를 가져오고 .GetNextPage() 와 같은
추가 헬퍼 메서드를 가진 표준 응답 객체를 받을 수도 있다. 예:
page, err := client.Messages.Batches.List(context.TODO(), anthropic.MessageBatchListParams{
	Limit: anthropic.Int(20),
})
for page != nil {
	for _, batch := range page.Data {
		fmt.Printf("%+v\n", batch)
	}
	page, err = page.GetNextPage()
}
if err != nil {
	panic(err.Error())
}
오류(Errors)
API가 비성공 status code를 반환하면, 우리는 *anthropic.Error 타입의 오류를 반환한다.
이는 요청의 StatusCode, *http.Request, *http.Response 값과
오류 본문의 JSON을 포함한다(SDK의 다른 응답 객체와 유사하게). 오류에는 또한 응답 헤더의
RequestID 가 포함되며, 이는 Anthropic 지원팀과의 트러블슈팅에 유용하다.
오류 처리를 위해 errors.As 패턴 사용을 권장한다:
_, err := client.Messages.New(context.TODO(), anthropic.MessageNewParams{
	MaxTokens: 1024,
	Messages: []anthropic.MessageParam{{
		Content: []anthropic.ContentBlockParamUnion{{
			OfText: &anthropic.TextBlockParam{
				Text: "x",
			},
		}},
		Role: anthropic.MessageParamRoleUser,
	}},
	Model: anthropic.ModelClaudeSonnet4_5_20250929,
})
if err != nil {
	var apierr *anthropic.Error
	if errors.As(err, &apierr) {
		println("Request ID:", apierr.RequestID)
		println(string(apierr.DumpRequest(true)))  // Prints the serialized HTTP request
		println(string(apierr.DumpResponse(true))) // Prints the serialized HTTP response
	}
	panic(err.Error()) // GET "/v1/messages": 400 Bad Request (Request-ID: req_xxx) { ... }
}
다른 오류가 발생하면 wrapping 되지 않은 상태로 반환된다. 예를 들어,
HTTP transport가 실패하면 *net.OpError 를 wrapping 한 *url.Error 를 받을 수 있다.
타임아웃(Timeouts)
요청은 기본적으로 타임아웃되지 않는다. 요청 라이프사이클의 타임아웃을 설정하려면 context를 사용한다.
요청이 재시도될 경우 context 타임아웃은 처음부터 다시 시작되지 않는다는 점에 주의한다.
재시도당 타임아웃을 설정하려면 option.WithRequestTimeout() 을 사용한다.
// This sets the timeout for the request, including all the retries.
ctx, cancel := context.WithTimeout(context.Background(), 5*time.Minute)
defer cancel()
client.Messages.New(
	ctx,
	anthropic.MessageNewParams{
		MaxTokens: 1024,
		Messages: []anthropic.MessageParam{{
			Content: []anthropic.ContentBlockParamUnion{{
				OfText: &anthropic.TextBlockParam{
					Text: "What is a quaternion?",
				},
			}},
			Role: anthropic.MessageParamRoleUser,
		}},
		Model: anthropic.ModelClaudeSonnet4_5_20250929,
	},
	// This sets the per-retry timeout
	option.WithRequestTimeout(20*time.Second),
)
긴 요청(Long Requests)
중요더 오래 실행되는 요청에 대해서는 streaming Messages API 사용을 강력히 권장한다.

streaming을 사용하지 않고 큰 MaxTokens 값을 설정하는 것은 권장하지 않는다. 일부 네트워크는 일정 시간이 지나면 idle 커넥션을 끊을 수 있으며,
이로 인해 Anthropic으로부터 응답을 받지 못한 채 요청이 실패하거나 타임아웃될 수 있다.
이 SDK는 또한 non-streaming 요청이 약 10분 이상 걸릴 것으로 예상되면 오류를 반환한다.
.Messages.NewStreaming() 을 호출하거나 커스텀 타임아웃을 설정하면 이 오류가 비활성화된다.
파일 업로드(File uploads)
multipart 요청에서 파일 업로드에 해당하는 요청 파라미터는
io.Reader 로 타이핑된다. io.Reader 의 내용은 기본적으로 파일명 "anonymous_file" 과
content-type "application/octet-stream" 으로 multipart form
파트로 전송된다. 따라서 우리가 제공하는 anthropic.File(reader io.Reader, filename string, contentType string)
헬퍼로 io.Reader 를 적절한 파일명과 content type으로 손쉽게 wrapping 하여 항상 커스텀 content-type을 지정할 것을 권장한다.
// A file from the file system
file, err := os.Open("/path/to/file.json")
anthropic.BetaFileUploadParams{
	File: anthropic.File(file, "custom-name.json", "application/json"),
	Betas: []anthropic.AnthropicBeta{anthropic.AnthropicBetaFilesAPI2025_04_14},
}

// A file from a string
anthropic.BetaFileUploadParams{
	File: anthropic.File(strings.NewReader("my file contents"), "custom-name.json", "application/json"),
	Betas: []anthropic.AnthropicBeta{anthropic.AnthropicBetaFilesAPI2025_04_14},
}
파일명과 content-type은 io.Reader 의 런타임 타입에 Name() string 또는 ContentType() string 을 구현하여 커스터마이즈할 수도 있다. os.File 은 Name() string 을 구현하므로,
os.Open 으로 반환된 파일은 디스크상의 파일명으로 전송된다.
재시도(Retries)
특정 오류는 기본적으로 짧은 지수 백오프와 함께 2번 자동 재시도된다.
기본적으로 모든 connection error, 408 Request Timeout, 409 Conflict, 429 Rate Limit,
그리고 >=500 Internal 오류를 재시도한다.
WithMaxRetries 옵션으로 이를 설정하거나 비활성화할 수 있다:
// Configure the default for all requests:
client := anthropic.NewClient(
	option.WithMaxRetries(0), // default is 2
)

// Override per-request:
client.Messages.New(
	context.TODO(),
	anthropic.MessageNewParams{
		MaxTokens: 1024,
		Messages: []anthropic.MessageParam{{
			Content: []anthropic.ContentBlockParamUnion{{
				OfText: &anthropic.TextBlockParam{
					Text: "What is a quaternion?",
				},
			}},
			Role: anthropic.MessageParamRoleUser,
		}},
		Model: anthropic.ModelClaudeSonnet4_5_20250929,
	},
	option.WithMaxRetries(5),
)
raw 응답 데이터에 접근하기 (예: 응답 헤더)
option.WithResponseInto() 요청 옵션을 사용해 raw HTTP 응답 데이터에 접근할 수 있다. 이는
응답 헤더, status code 또는 기타 세부 정보를 확인해야 할 때 유용하다.
// Create a variable to store the HTTP response
var response *http.Response
message, err := client.Messages.New(
	context.TODO(),
	anthropic.MessageNewParams{
		MaxTokens: 1024,
		Messages: []anthropic.MessageParam{{
			Content: []anthropic.ContentBlockParamUnion{{
				OfText: &anthropic.TextBlockParam{
					Text: "x",
				},
			}},
			Role: anthropic.MessageParamRoleUser,
		}},
		Model: anthropic.ModelClaudeSonnet4_5_20250929,
	},
	option.WithResponseInto(&response),
)
if err != nil {
	// handle error
}
fmt.Printf("%+v\n", message)

fmt.Printf("Status Code: %d\n", response.StatusCode)
fmt.Printf("Headers: %+#v\n", response.Header)
커스텀/문서화되지 않은 요청 만들기
이 라이브러리는 문서화된 API에 편리하게 접근할 수 있도록 타이핑되어 있다. 문서화되지 않은
endpoint, 파라미터 또는 응답 속성에 접근해야 하는 경우에도 이 라이브러리를 사용할 수 있다.
문서화되지 않은 endpoint
문서화되지 않은 endpoint로 요청을 보내려면 client.Get, client.Post 및 기타 HTTP verb를 사용할 수 있다.
이러한 요청을 만들 때 client의 RequestOptions(예: 재시도)는 그대로 적용된다.
var (
    // params can be an io.Reader, a []byte, an encoding/json serializable object,
    // or a "…Params" struct defined in this library.
    params map[string]any

    // result can be an []byte, *http.Response, a encoding/json deserializable object,
    // or a model defined in this library.
    result *http.Response
)
err := client.Post(context.Background(), "/unspecified", params, &result)
if err != nil {
    …
}
문서화되지 않은 요청 파라미터
문서화되지 않은 파라미터를 사용해 요청을 보내려면 option.WithQuerySet()
또는 option.WithJSONSet() 메서드를 사용할 수 있다.
params := FooNewParams{
    ID:   "id_xxxx",
    Data: FooNewParamsData{
        FirstName: anthropic.String("John"),
    },
}
client.Foo.New(context.Background(), params, option.WithJSONSet("data.last_name", "Doe"))
문서화되지 않은 응답 속성
문서화되지 않은 응답 속성에 접근하려면, result.JSON.RawJSON() 으로 응답의 raw JSON에 문자열로 접근하거나,
result.JSON.Foo.Raw() 로 결과의 특정 필드의 raw JSON을 가져올 수 있다.
응답 struct에 존재하지 않는 필드는 저장되며 result.JSON.ExtraFields() 로 접근할 수 있는데, 이는 추가 필드를 map[string]Field 로 반환한다.
미들웨어(Middleware)
주어진 미들웨어를 요청에 적용하는 option.WithMiddleware 를 제공한다.
func Logger(req *http.Request, next option.MiddlewareNext) (res *http.Response, err error) {
	// Before the request
	start := time.Now()
	LogReq(req)

	// Forward the request to the next handler
	res, err = next(req)

	// Handle stuff after the request
	end := time.Now()
	LogRes(res, err, start - end)

    return res, err
}

client := anthropic.NewClient(
	option.WithMiddleware(Logger),
)
여러 미들웨어가 가변 인자로 제공되면 미들웨어는 좌에서 우로 적용된다.
option.WithMiddleware 가 여러 번 주어지면, 예를 들어 먼저 client에서 그리고 메서드에서 주어지면,
client의 미들웨어가 먼저 실행되고 메서드에서 주어진 미들웨어가
다음에 실행된다.
기본 http.Client 를 option.WithHTTPClient(client) 로 교체할 수도 있다. 오직 하나의 http client만
허용되며(이는 이전 client를 덮어쓴다), 모든 미들웨어가 적용된 후 요청을 받는다.
Amazon Bedrock
이 라이브러리를 Amazon Bedrock 과 함께 사용하려면,
기본 config를 읽는 bedrock 요청 옵션 bedrock.WithLoadDefaultConfig(…) 를
사용한다.
bedrock 라이브러리를 import 하면 streaming을 위한 application/vnd.amazon.eventstream 디코더도
전역적으로 등록된다.
package main

import (
	"github.com/anthropics/anthropic-sdk-go"
	"github.com/anthropics/anthropic-sdk-go/bedrock"
)

func main() {
	client := anthropic.NewClient(
		bedrock.WithLoadDefaultConfig(context.Background()),
	)
}
이미 aws.Config 가 있다면 bedrock.WithConfig(cfg) 로 직접 사용할 수도 있다.
Bearer Token 인증(Bearer Token Authentication)
AWS credentials 대신 bearer token으로 Bedrock에 인증할 수도 있다. 이는 팀이 AWS credentials, IAM role 또는 계정 수준 권한을 관리하지 않고도 Bedrock에 접근해야 하는 기업 환경에서 유용하다.
가장 간단한 방법은 AWS_BEARER_TOKEN_BEDROCK 환경 변수를 설정하는 것이다:
package main

import (
	"context"

	"github.com/anthropics/anthropic-sdk-go"
	"github.com/anthropics/anthropic-sdk-go/bedrock"
)

func main() {
	// Automatically uses AWS_BEARER_TOKEN_BEDROCK from the environment.
	// Region defaults to us-east-1 or uses AWS_REGION if set.
	client := anthropic.NewClient(
		bedrock.WithLoadDefaultConfig(context.Background()),
	)
}
프로그래밍 방식으로 token을 제공하려면 BearerAuthTokenProvider 와 함께 bedrock.WithConfig 를 사용한다:
package main

import (
	"context"

	"github.com/anthropics/anthropic-sdk-go"
	"github.com/anthropics/anthropic-sdk-go/bedrock"
	"github.com/aws/aws-sdk-go-v2/aws"
)

func main() {
	cfg := aws.Config{
		Region:                  "us-west-2",
		BearerAuthTokenProvider: bedrock.NewStaticBearerTokenProvider("your-bearer-token"),
	}
	client := anthropic.NewClient(
		bedrock.WithConfig(cfg),
	)
}
Anthropic과 Amazon Bedrock에 대해 자세히 보려면 here, Bedrock API key에 대해서는 here 를 참고한다.
Google Vertex AI
이 라이브러리를 Google Vertex AI 와 함께 사용하려면,
Application Default Credentials 를 읽는 요청 옵션 vertex.WithGoogleAuth(…) 를
사용한다.
package main

import (
	"context"

	"github.com/anthropics/anthropic-sdk-go"
	"github.com/anthropics/anthropic-sdk-go/vertex"
)

func main() {
	client := anthropic.NewClient(
		vertex.WithGoogleAuth(context.Background(), "us-central1", "id-xxx"),
	)
}
이미 *google.Credentials 가 있다면
vertex.WithCredentials(ctx, region, projectId, creds) 로 직접 사용할 수도 있다.
Anthropic과 Google Vertex에 대해 자세히 보려면 here 를 참고한다.
시맨틱 버저닝(Semantic versioning)
이 패키지는 일반적으로 SemVer 컨벤션을 따르지만, 특정 backwards-incompatible 변경 사항이 minor 버전으로 릴리스될 수 있다:

기술적으로 public이지만 외부 사용을 위해 의도되거나 문서화되지 않은 라이브러리 내부에 대한 변경. (만약 그러한 내부에 의존하고 있다면 GitHub issue를 열어 알려 주기 바란다.)
실제로 대다수 사용자에게 영향을 미치지 않을 것으로 예상되는 변경.

우리는 backwards-compatibility를 진지하게 받아들이고 매끄러운 업그레이드 경험에 의존할 수 있도록 노력하고 있다.
여러분의 피드백을 환영한다. 질문, 버그 또는 제안은 issue로 열어 주기 바란다.
기여(Contributing)
contributing 문서를 참고한다.
